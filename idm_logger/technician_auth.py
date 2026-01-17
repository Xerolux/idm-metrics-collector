# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Xerolux
#
# This file contains encrypted logic for IDM Heat Pump authentication.
# The code is obfuscated to protect the authentication algorithm implementation.

from cryptography.fernet import Fernet

# Encrypted payload containing the technician code generation logic
_PAYLOAD = b"gAAAAABpZpu99iZL1togZnYCNBbiIiNrxrGuSkNnYUfRG1nL5JbHoTkeMjPkgdJcJZzX0VZC5-uGpXh9B9m9HVw3t2Fd3FyufU4uFsaBJDALpvrf3ZKMj4fgC0mvD7CMtUjtxx8qAFHGiHG9omleEfGAcsra9JxEHAlmR7l1OCk0Tne5rQCXT5EwgUrk8wW2e_I43FGngb43yGpwPLzl5_z5T00s9_FaTzrOaUAH34QwvdwNrHkHHKj4ARZbYTtKPNbYIHTQg8CqFmd5kxC7CyzIbW8mw_1KgA789pOBSyj5vuGbnVoWqZo4iKCj1k_eJB7XyHN5mWX1WkPOrC_PYJJOVKtgHtfMj95xGzAJQmycvIkbrxHEIoHXSToP8WMIHK6JLDsWDQFZAo34obz3C6HIrS-G1OcjAxVlvVEXOJax-iLmfbdcEvpd4uB1XDbqdWLLyOVYw5RNWDxHv6k27ybn1APivlJDgIMtKZOMl-KaDeXrb2Gsg2Y81EKAUagdQ1PrILty_HGWgkhaWnUBq1XUXuUcKB4IIAGUb27R-IOlmYVq0HCsV1X8JgDWAQFKs38x6egvmGy7GXDUL2WLwigR6EE5peNN1ZG0fapRotMS58V6HUF1Sa-irRQZPXD5I95rMceS42YvoWwsW4zqGvZm4AAANZmQWrMPE2-bpAYY7Ly5UxubgUUqrt1LmrjAu_a6Ob4J3dX_2VYQqnJ_1UdWTom25hp4kf9nqzY75IhNS-UWDAchfeEg__ntdnsYW7JVR7PR_XXQgk2XW953puZrF5Vy9t_orG2Vwj50Lwh9aaWDJ-6ZwfaoVUMYiiArzG28HctSgTlJDCslUPCGljEs5DF_bjw-Xg=="


def _get_key():
    # Key reconstruction for in-memory decryption
    # Part 1: iYYeyAs
    k1 = "iYYeyAs"
    # Part 2: 9MbBuLxzH
    k2 = "9MbBuLxzH"
    # Part 3: Anacdiqd2h9f
    k3 = "Anacdiqd2h9f"
    # Part 4: N4UaeAYKPHxYZ0E=
    k4 = "N4UaeAYKPHxYZ0E="
    return (k1 + k2 + k3 + k4).encode()


try:
    _cipher_suite = Fernet(_get_key())
    _decrypted_code = _cipher_suite.decrypt(_PAYLOAD)
    exec(_decrypted_code)
except Exception:
    # Fail silently or generic error to prevent analysis
    print("Authentication logic error")
    pass
