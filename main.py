"""
    Main Program Entry Point
"""
import time
import datetime
import logging
import argparse
import sys
import os
from appdirs import AppDirs

from slot_finder import ChromeAmazonSlotFinder
from notifications import NotificationService
from database import UserConfiguration


SLEEP_TIME_SECONDS = 300
EXECUTION_DATE_TIME_FORMAT = '%m-%d-%Y %H:%M:%S'

LOGGER = logging.getLogger(__name__)
USER_CONFIGURATION = UserConfiguration()


def send_notification(message: str):
    """ Send a user notification """
    url = USER_CONFIGURATION.get_notification_subscription_url()

    if not url:
        configure_user_notifications()
        url = USER_CONFIGURATION.get_notification_subscription_url()


    notification_service = NotificationService(url)
    notification_service.send(message)

def run_slot_check():
    """ Runs the main loop for checking delivery slots"""
    parser = ChromeAmazonSlotFinder()
    parser.login()

    while True:
        #pylint:disable-msg=C0301
        print(f'{datetime.datetime.now().strftime(EXECUTION_DATE_TIME_FORMAT)} - Checking time slots')
        LOGGER.debug('Checking time slots')
        available_dates = parser.get_available_dates()
        if len(available_dates) == 0:
            LOGGER.debug('No time slots available')
            print('No time slots available')
        else:
            print('Time slots available')
            send_notification(f'Time Slots Available: {",".join(available_dates)}')
            LOGGER.debug('Time slots available')
            for date in available_dates:
                LOGGER.debug('Slot - %s', date)
                print(f'Slot - {date}')
        time.sleep(SLEEP_TIME_SECONDS)
        parser.refresh_page()

def configure_user_notifications():
    """ Configure the notification service url """
    print('Retrieving notification url...')
    url = NotificationService.get_new_subscription_url()
    USER_CONFIGURATION.set_notification_subscription(url)
    print(f'Please open this url to subscribe to notifications {url}')

def dump_all_notifications(limit: int):
    """ Dump the N most recent notifications """
    notifications = USER_CONFIGURATION.get_all_n_notifications(limit)
    # Aren't you happy I know list comprehensions
    #pylint:disable-msg=C0301
    # Let this monstrosity grow
    LOGGER.debug(f'Dumping the past {limit} notifications: {[",".join(notification) for notification in notifications]}')
    if not notifications:
        print('No notification history!')
    else:
        for user_notification in notifications:
            print(f'{user_notification[0]} - {user_notification[1]}')

def delete_notifications():
    """ Delete the local notification history """
    print('Deleting all past notifications')
    LOGGER.debug('Delete all past notifications')
    USER_CONFIGURATION.delete_all_notifications()

def main(argv):
    """ Main application entry point """
    USER_CONFIGURATION.setup()

    parser = argparse.ArgumentParser(description='Find open delivery slots')
    #pylint:disable-msg=C0301
    parser.add_argument("-l", "--log-level", help="Set the log level to TRACE, DEBUG, INFO, WARN, ERROR", type=str)
    parser.add_argument("-n", "--notifications", help="Setup Nofications", action="store_true")
    parser.add_argument("-tn", "--test-notification", help="Send a test notification", action="store_true")
    #pylint:disable-msg=C0301
    parser.add_argument("-dn", "--dump-notifications", help="Dumps the previous N notifications", type=int)
    parser.add_argument("-cn", "--clear-notifications", help="Clears all notifications from the local history", action="store_true")
    args = parser.parse_args()

    loglevel = 'WARN'
    configure_notifications = False
    dump_notifications = False
    send_test_notification = False
    delete_all_notifications = False
    limit = 0

    if args.log_level:
        loglevel = args.log_level
    if args.notifications:
        configure_notifications = True
    elif args.test_notification:
        send_test_notification = True
    elif args.dump_notifications:
        dump_notifications = True
        limit = args.dump_notifications
    elif args.clear_notifications:
        delete_all_notifications = True

    numeric_level = getattr(logging, loglevel.upper().strip(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    dirs = AppDirs("SlotFinder", "Bryan")
    logging.basicConfig(format='%(asctime)s %(module)s %(levelname)s: %(message)s',
                        datefmt=EXECUTION_DATE_TIME_FORMAT,
                        level=numeric_level,
                        filename=os.path.join(dirs.user_data_dir, 'slot_finder.log'))

    if configure_notifications:
        configure_user_notifications()
    elif dump_notifications:
        dump_all_notifications(limit)
    elif send_test_notification:
        print('Sending Test Notification: This is a test notification')
        send_notification('This is a test notification')
    elif delete_all_notifications:
        delete_notifications()
    else:
        run_slot_check()

if __name__ == "__main__":
    main(sys.argv[1:])
