
from datetime import datetime
from unittest.mock import patch
from idm_logger.technician_auth import calculate_codes

def test_technician_code_generation():
    # Test case 1: 2023-10-27 14:30
    # Day: 27
    # Month: 10
    # Year: 2023
    # Hour: 14

    fixed_date = datetime(2023, 10, 27, 14, 30)

    with patch('idm_logger.technician_auth.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_date

        codes = calculate_codes()

        # Level 1: DDMM -> 2710
        assert codes["level_1"] == "2710"

        # Level 2: {hh_last}{hh_first}{year_last}{month_last}{day_last}
        # Hour: 14 -> hh_first=1, hh_last=4
        # Year: 2023 -> year_last=3
        # Month: 10 -> month_last=0
        # Day: 27 -> day_last=7
        # Result: 41307

        assert codes["level_2"] == "41307"

def test_technician_code_single_digit_hour():
    # Test case 2: 2024-05-05 09:15
    # Day: 05
    # Month: 05
    # Year: 2024
    # Hour: 09

    fixed_date = datetime(2024, 5, 5, 9, 15)

    with patch('idm_logger.technician_auth.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_date

        codes = calculate_codes()

        # Level 1: DDMM -> 0505
        assert codes["level_1"] == "0505"

        # Level 2: {hh_last}{hh_first}{year_last}{month_last}{day_last}
        # Hour: 09 -> hh_first=0, hh_last=9
        # Year: 2024 -> year_last=4
        # Month: 5 -> month_last=5
        # Day: 5 -> day_last=5
        # Result: 90455

        assert codes["level_2"] == "90455"
