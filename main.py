"""
    Main Program Entry Point
"""
import time
import datetime

from slot_finder import ChromeAmazonSlotFinder

SLEEP_TIME_SECONDS = 300
EXECUTION_DATE_TIME_FORMAT = '%m-%d-%Y %H:%M:%S'

parser = ChromeAmazonSlotFinder()
parser.login()

while True:
    print(f'Checking time slots {datetime.date.today().strftime(EXECUTION_DATE_TIME_FORMAT)}')
    parser.refresh_page()
    parser.parse_with_beautiful_soup()
    available_dates = parser.get_available_dates()
    if len(available_dates) == 0:
        print('No time slots available')
    else:
        print('Time slots available')
        for date in available_dates:
            print(f'Slot - {date}')
    time.sleep(SLEEP_TIME_SECONDS)
