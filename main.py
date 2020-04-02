"""
    Main Program Entry Point
"""
import time
import datetime
import logging
import getopt
import sys

from slot_finder import ChromeAmazonSlotFinder

SLEEP_TIME_SECONDS = 300
EXECUTION_DATE_TIME_FORMAT = '%m-%d-%Y %H:%M:%S'

logger = logging.getLogger(__name__)


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"l:i",["loglevel="])
    except getopt.GetoptError:
        print ('main.py -l LOGLEVEL')
        sys.exit(2)

    loglevel = 'WARN'
    for opt, arg in opts:
      if opt == '-h':
         print ('main.py --loglevel=[]')
         sys.exit()
      elif opt in ("-l", "--loglevel"):
         loglevel = arg

    numeric_level = getattr(logging, loglevel.upper().strip(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                        datefmt=EXECUTION_DATE_TIME_FORMAT, 
                        level=numeric_level, 
                        filename='slot_finder.log')

    parser = ChromeAmazonSlotFinder()
    parser.login()

    while True:
        print(f'{datetime.datetime.now().strftime(EXECUTION_DATE_TIME_FORMAT)} - Checking time slots')
        logger.debug('Checking time slots')
        parser.refresh_page()
        parser.parse_with_beautiful_soup()
        available_dates = parser.get_available_dates()
        if len(available_dates) == 0:
            logger.debug('No time slots available')
            print('No time slots available')
        else:
            print('Time slots available')
            logger.debug('Time slots available')
            for date in available_dates:
                logger.debug(f'Slot - {date}')
                print(f'Slot - {date}')
        time.sleep(SLEEP_TIME_SECONDS)


if __name__ == "__main__":
   main(sys.argv[1:])