import hmac as hm
from secrets import compare_digest

expected = b"expected"
actual = b"actual"
hm.compare_digest(expected, actual)
compare_digest(expected, actual)
