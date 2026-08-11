from __future__ import annotations

CATEGORY_LABELS = {
    "cryptography": "암호화",
    "process-security": "프로세스 보안",
    "deserialization": "안전한 역직렬화",
}

RULES = [
    {
        "id": "GOOD004",
        "name": "Constant-Time Secret Comparison",
        "category": "cryptography",
        "confidence": "HIGH",
        "good": "hmac.compare_digest(provided, expected)",
        "bad": "provided == expected",
        "ref": "비밀값 비교에 일정 시간 비교 함수를 사용합니다.",
    },
    {
        "id": "GOOD005",
        "name": "Safer Subprocess Invocation",
        "category": "process-security",
        "confidence": "HIGH",
        "good": 'subprocess.run(["git", "status"], shell=False)',
        "bad": 'subprocess.run("git status", shell=True)',
        "ref": "명령과 인자를 분리하고 shell 실행을 사용하지 않습니다.",
    },
    {
        "id": "GOOD006",
        "name": "Safe YAML Deserialization",
        "category": "deserialization",
        "confidence": "HIGH",
        "good": "yaml.safe_load(document)",
        "bad": "yaml.load(document)",
        "ref": "임의 객체 생성을 피하는 안전한 YAML 로더를 사용합니다.",
    },
]
