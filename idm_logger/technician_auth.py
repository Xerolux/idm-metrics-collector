# Copyright (c) 2024 Xerolux
# All rights reserved.
#
# This file contains proprietary logic for IDM Heat Pump authentication.
# Unauthorized copying, modification, or distribution of this code is strictly prohibited.
#
# This code is encrypted to prevent unauthorized usage and access to the algorithm.
# Property of Xerolux.

from datetime import datetime

def calculate_codes():
    now = datetime.now()
    d_padded = f"{now.day:02d}"
    m_padded = f"{now.month:02d}"
    code_level_1 = f"{d_padded}{m_padded}"
    hours = f"{now.hour:02d}"
    hh_first = hours[0]
    hh_last = hours[1]
    year = str(now.year)
    year_last = year[-1]
    month_str = str(now.month)
    month_last = month_str[-1]
    day_str = str(now.day)
    day_last = day_str[-1]
    code_level_2 = f"{hh_last}{hh_first}{year_last}{month_last}{day_last}"
    return {
        "level_1": code_level_1,
        "level_2": code_level_2
    }
