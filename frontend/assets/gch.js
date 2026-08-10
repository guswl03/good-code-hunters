/* ────────────────────────────────────────────────────────────
   착한코드검거단 — 공통 모듈 (규칙 / 스캐너 / 저장소 / 랭킹)
   ※ 실제 제품의 탐지 엔진은 Python ast 모듈 기반이다. 이 브라우저
     프로토타입은 동일한 Finding 스키마를 유지한 채 구문 단위
     스캐너로 근사 동작하며, 대상 코드를 실행하지 않는다.
   ──────────────────────────────────────────────────────────── */
(function (global) {
  "use strict";

  const CATEGORIES = {
    "injection-prevention": "인젝션 방어",
    "cryptography": "암호학",
    "credential-protection": "자격증명 보호",
    "side-channel-defense": "부채널 방어",
    "command-execution": "명령 실행",
    "deserialization": "역직렬화"
  };

  const RULES = [
    {
      id: "GOOD001", name: "Parameterized SQL Query", ko: "쿼리와 파라미터를 분리한 SQL 실행",
      category: "injection-prevention", tier: "P0",
      why: "SQL 문자열과 사용자 입력을 분리해 드라이버가 값을 바인딩하도록 맡기고 있습니다. 문자열 결합이나 f-string으로 쿼리를 조립하지 않기 때문에 입력값이 SQL 구문으로 해석될 여지가 없습니다.",
      ref: "CWE-89 · OWASP Top 10 A03:2021 Injection",
      good: 'cursor.execute(\n    "SELECT * FROM users WHERE id = ?",\n    (user_id,),\n)',
      bad: 'cursor.execute(\n    f"SELECT * FROM users WHERE id = {user_id}"\n)',
      test(stmt) {
        if (!/\.\s*execute(many)?\s*\(/.test(stmt)) return false;
        if (/f["']|%\s*\(|\+\s*(str\(|[a-zA-Z_])|\.format\s*\(/.test(stmt)) return false;
        const hasPlaceholder = /["'][^"']*(\?|%s|:[a-zA-Z_]\w*)[^"']*["']/.test(stmt);
        const hasParamArg = /["']\s*,\s*[\(\[\{a-zA-Z_]/.test(stmt);
        return hasPlaceholder && hasParamArg;
      }
    },
    {
      id: "GOOD002", name: "Cryptographically Secure Randomness", ko: "보안용 난수에 secrets 모듈 사용",
      category: "cryptography", tier: "P0",
      why: "예측 가능한 random 모듈 대신 OS의 CSPRNG를 사용하는 secrets API로 값을 만들고 있습니다. 세션 토큰·비밀번호 재설정 링크처럼 추측되면 안 되는 값에 적합한 선택입니다.",
      ref: "CWE-338 · Python docs: secrets — Generate secure tokens",
      good: "token = secrets.token_urlsafe(32)",
      bad: "token = str(random.random())",
      test: (s) => /\bsecrets\s*\.\s*(token_bytes|token_hex|token_urlsafe|randbelow|choice|SystemRandom)\b/.test(s)
    },
    {
      id: "GOOD003", name: "Password Hashing / KDF", ko: "비밀번호에 전용 해시·KDF 사용",
      category: "credential-protection", tier: "P0",
      why: "비밀번호를 md5/sha1 같은 범용 고속 해시가 아니라 의도적으로 느린 KDF로 처리하고 있습니다. 솔트와 반복 횟수를 통해 유출 시 대량 크래킹 비용을 크게 끌어올립니다.",
      ref: "CWE-916 · OWASP Password Storage Cheat Sheet",
      good: 'digest = hashlib.pbkdf2_hmac(\n    "sha256", password, salt, 390_000\n)',
      bad: "digest = hashlib.md5(password).hexdigest()",
      test: (s) => /\bhashlib\s*\.\s*(pbkdf2_hmac|scrypt)\b|\bbcrypt\s*\.\s*(hashpw|kdf)\b|PasswordHasher\s*\([^)]*\)\s*\.\s*hash\b|\bph\s*\.\s*hash\s*\(/.test(s)
    },
    {
      id: "GOOD004", name: "Constant-Time Secret Comparison", ko: "비밀값 비교에 상수 시간 API 사용",
      category: "side-channel-defense", tier: "P0",
      why: "토큰·서명값을 == 로 비교하면 일치하는 앞부분 길이에 따라 응답 시간이 달라져 값이 한 바이트씩 추측될 수 있습니다. compare_digest는 길이와 무관하게 일정한 시간으로 비교합니다.",
      ref: "CWE-208 · Python docs: hmac.compare_digest",
      good: "if hmac.compare_digest(received, expected):\n    ...",
      bad: "if received == expected:\n    ...",
      test: (s) => /\b(hmac|secrets)\s*\.\s*compare_digest\s*\(/.test(s)
    },
    {
      id: "GOOD005", name: "Safer Subprocess Invocation", ko: "인자 리스트로 전달하는 subprocess 호출",
      category: "command-execution", tier: "P0",
      why: "명령을 하나의 셸 문자열이 아니라 인자 리스트로 넘기고 shell=True를 쓰지 않았습니다. 세미콜론·파이프·백틱 같은 셸 메타문자가 해석되지 않으므로 명령 주입 경로가 차단됩니다.",
      ref: "CWE-78 · Python docs: subprocess Security Considerations",
      good: 'subprocess.run(\n    ["git", "status"], shell=False, check=True\n)',
      bad: 'subprocess.run(\n    "git status " + branch, shell=True\n)',
      test(stmt) {
        if (!/\bsubprocess\s*\.\s*(run|Popen|check_output|check_call)\s*\(/.test(stmt)) return false;
        if (/shell\s*=\s*True/.test(stmt)) return false;
        return /\(\s*\[|\(\s*\(/.test(stmt.replace(/\bsubprocess\s*\.\s*\w+\s*/, "sub"));
      }
    },
    {
      id: "GOOD006", name: "Safe YAML Deserialization", ko: "안전한 로더로 YAML 역직렬화",
      category: "deserialization", tier: "P0",
      why: "임의의 Python 객체를 생성할 수 있는 yaml.load(Loader=Loader) 대신 안전한 로더를 사용했습니다. 신뢰할 수 없는 YAML이 들어와도 객체 생성을 통한 코드 실행으로 이어지지 않습니다.",
      ref: "CWE-502 · PyYAML: loading YAML safely",
      good: "data = yaml.safe_load(text)",
      bad: "data = yaml.load(text, Loader=yaml.Loader)",
      test: (s) => /\byaml\s*\.\s*safe_load(_all)?\s*\(/.test(s) || /\byaml\s*\.\s*load\s*\([^)]*Loader\s*=\s*(yaml\s*\.\s*)?(SafeLoader|CSafeLoader)/.test(s)
    }
  ];

  const P1_RULES = [
    {
      id: "GOOD007", name: "Secure TLS Context", ko: "안전한 기본값의 TLS 컨텍스트",
      category: "cryptography", tier: "P1",
      why: "인증서 검증과 호스트명 확인이 켜진 기본 컨텍스트를 사용합니다. verify_mode를 CERT_NONE으로 낮추거나 검증을 끄는 코드와 대비됩니다.",
      good: "context = ssl.create_default_context()",
      bad: "context.verify_mode = ssl.CERT_NONE",
      ref: "CWE-295 · Python docs: ssl.create_default_context"
    },
    {
      id: "GOOD008", name: "Path Traversal Defense", ko: "경로 조작 방어",
      category: "injection-prevention", tier: "P1",
      why: "사용자 입력으로 만들어진 경로를 정규화한 뒤 허용된 기준 디렉터리 안에 있는지 확인합니다. ../ 를 통한 상위 디렉터리 탈출을 차단합니다.",
      good: "resolved = (base / user_path).resolve()\nresolved.relative_to(base)",
      bad: 'open(base + "/" + user_path)',
      ref: "CWE-22 · OWASP Path Traversal"
    }
  ];

  /* ── 샘플 파일 ─────────────────────────── */
  const SAMPLE_NAME = "payment_service.py";
  const SAMPLE_SRC = `"""결제 서비스 — 사용자 인증 및 정산 처리."""

import hashlib
import hmac
import secrets
import sqlite3
import subprocess

import yaml

CONFIG_PATH = "config/payment.yml"


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fp:
        return yaml.safe_load(fp.read())


def find_user(conn: sqlite3.Connection, user_id: str):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, pw_hash, salt FROM users WHERE id = ?",
        (user_id,),
    )
    return cursor.fetchone()


def issue_session_token() -> str:
    """세션 토큰 발급."""
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> tuple[bytes, bytes]:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        390_000,
    )
    return digest, salt


def verify_webhook(payload: bytes, signature: str, secret: bytes) -> bool:
    expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def sync_ledger(branch: str) -> int:
    result = subprocess.run(
        ["git", "pull", "--ff-only", "origin", branch],
        shell=False,
        check=True,
        capture_output=True,
    )
    return result.returncode


def audit_log(entries: list[str]) -> None:
    for entry in entries:
        print(f"[audit] {entry}")
`;

  /* ── 스캐너 ────────────────────────────── */
  function logicalStatement(lines, i) {
    let depth = 0, out = "";
    for (let k = i; k < Math.min(lines.length, i + 12); k++) {
      const line = lines[k].split("#")[0];
      out += line + " ";
      for (const ch of line) {
        if ("([{".includes(ch)) depth++;
        else if (")]}".includes(ch)) depth--;
      }
      if (depth <= 0) break;
    }
    return out;
  }

  function scan(source) {
    const lines = source.split(/\r?\n/);
    const findings = [];
    const seen = new Set();

    const openers = (source.match(/[\(\[\{]/g) || []).length;
    const closers = (source.match(/[\)\]\}]/g) || []).length;
    if (openers - closers > 2) {
      const err = new Error("괄호가 닫히지 않은 것으로 보입니다. 파일의 문법을 확인해주세요.");
      err.userFacing = true;
      throw err;
    }

    lines.forEach((raw, idx) => {
      const codeOnly = raw.split("#")[0];
      if (!codeOnly.trim()) return;
      const stmt = logicalStatement(lines, idx);
      for (const rule of RULES) {
        if (!rule.test(stmt) && !rule.test(codeOnly)) continue;
        const prev = idx > 0 ? lines[idx - 1].split("#")[0] : "";
        if (/[\(\[\{,]\s*$/.test(prev) && !rule.test(codeOnly)) continue;
        const key = rule.id + ":" + idx;
        if (seen.has(key)) continue;
        seen.add(key);
        findings.push({
          rule_id: rule.id, rule_name: rule.name, rule_name_ko: rule.ko,
          category: rule.category, line: idx + 1,
          column: raw.length - raw.trimStart().length,
          evidence: raw.trim(), explanation: rule.why, reference: rule.ref
        });
      }
    });

    findings.sort((a, b) => a.line - b.line || a.column - b.column || a.rule_id.localeCompare(b.rule_id));
    return { findings };
  }

  /* ── 저장소 (페이지 간 공유) ───────────── */
  const KEY = "gch.state.v1";
  const emptyState = () => ({ runs: 0, totalFinds: 0, history: [], last: null });

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      if (!raw) return emptyState();
      const s = JSON.parse(raw);
      return Object.assign(emptyState(), s);
    } catch (e) { return emptyState(); }
  }
  function save(s) {
    try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) { /* 저장 불가 환경 무시 */ }
  }
  function recordRun(fileName, findings, ms, source) {
    const s = load();
    s.runs += 1;
    s.totalFinds += findings.length;
    s.last = {
      file: fileName, at: Date.now(), ms,
      count: findings.length,
      cats: [...new Set(findings.map(f => f.category))],
      findings, source
    };
    s.history.unshift({ file: fileName, at: Date.now(), count: findings.length, cats: [...new Set(findings.map(f => f.category))].length });
    s.history = s.history.slice(0, 8);
    save(s);
    return s;
  }
  function reset() { save(emptyState()); }

  /* ── 랭킹 ──────────────────────────────── */
  const SAMPLE_RANKS = [
    { name: "hoxy_secure", team: "SecOps 스터디", finds: 128, cats: 6, hue: 78 },
    { name: "ast_walker", team: "코드리뷰 길드", finds: 111, cats: 6, hue: 300 },
    { name: "saltnpepper", team: "백엔드 4팀", finds: 97, cats: 5, hue: 258 },
    { name: "compare_dgst", team: "플랫폼 보안", finds: 74, cats: 5, hue: 190 },
    { name: "yaml_safe", team: "데브옵스", finds: 61, cats: 4, hue: 158 },
    { name: "pbkdf2_kim", team: "신입 부트캠프", finds: 43, cats: 4, hue: 30 },
    { name: "subproc_lee", team: "QA 자동화", finds: 28, cats: 3, hue: 220 },
    { name: "newbie_park", team: "학생 개발자", finds: 12, cats: 2, hue: 340 }
  ];
  const TIER_LABEL = { "t-king": "검거왕", "t-elite": "특급", "t-pro": "정예", "t-new": "신입" };
  function tierOf(n) {
    if (n >= 120) return "t-king";
    if (n >= 90) return "t-elite";
    if (n >= 25) return "t-pro";
    return "t-new";
  }
  function leaderboard() {
    const s = load();
    const lastCats = s.last ? s.last.cats.length : 0;
    const me = {
      me: true, name: "나 (이번 세션)",
      team: s.last ? s.last.file : "아직 분석 기록 없음",
      finds: s.totalFinds, cats: lastCats, hue: 258
    };
    const all = [...SAMPLE_RANKS.map(r => ({ ...r })), me].sort((a, b) => b.finds - a.finds || b.cats - a.cats);
    all.forEach((r, i) => { r.rank = i + 1; r.tier = tierOf(r.finds); });
    return all;
  }

  /* ── 유틸 ──────────────────────────────── */
  const escapeHtml = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  /* 아바타는 채도를 낮춘 중립 팔레트로 통일한다 — 색이 순위보다 튀지 않게 */
  const faceStyle = (r) => {
    if (r && r.me) return "background:#eaf2ff;color:#1b52a8;border-color:#c9dcf6";
    const hue = typeof r === "number" ? r : (r && r.hue) || 220;
    return `background:hsl(${hue} 14% 94%);color:hsl(${hue} 18% 36%)`;
  };
  const initials = (r) => r.me ? "ME" : (String(r.name).replace(/[^a-zA-Z가-힣]/g, "").slice(0, 2).toUpperCase() || "??");
  function timeAgo(ts) {
    const d = Math.round((Date.now() - ts) / 1000);
    if (d < 60) return "방금 전";
    if (d < 3600) return Math.floor(d / 60) + "분 전";
    if (d < 86400) return Math.floor(d / 3600) + "시간 전";
    return Math.floor(d / 86400) + "일 전";
  }
  function toast(msg) {
    let t = document.getElementById("toast");
    if (!t) {
      t = document.createElement("div");
      t.id = "toast";
      t.className = "toast";
      t.setAttribute("role", "status");
      t.setAttribute("aria-live", "polite");
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => t.classList.remove("show"), 2400);
  }

  global.GCH = {
    CATEGORIES, RULES, P1_RULES, SAMPLE_NAME, SAMPLE_SRC, SAMPLE_RANKS, TIER_LABEL,
    scan, load, save, recordRun, reset, leaderboard, tierOf,
    escapeHtml, faceStyle, initials, timeAgo, toast
  };
})(window);
