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
    if not USER_CONFIGURATION.get_notification_subscription_url():
        configure_user_notifications()

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
        time.sleep(UserConfiguration.get_refresh_time_seconds())
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

def view_current_refresh_rate():
    """ Print out the current refresh rate """
    current_refresh_time_seconds = USER_CONFIGURATION.get_refresh_time_seconds()
    print(f'Current Refresh Time: {get_minutes_from_seconds(current_refresh_time_seconds)} minutes')

def set_new_refresh_rate(refresh_rate_as_seconds: int):
    """ Set the input refresh rate """

    # Adding another check so the refresh rate is never less than 5 minutes
    refresh_rate_in_minutes = get_minutes_from_seconds(refresh_rate_as_seconds)
    if refresh_rate_as_seconds < UserConfiguration.DEFAULT_SLEEP_TIME_SECONDS:
        LOGGER.warning('Refresh rate cannot be set lower than 5 minutes: %s', refresh_rate_in_minutes)
        print(f'Refresh rate cannot be set lower than 5 minutes')
    else:
        print(f'Setting refresh rate to {refresh_rate_in_minutes} minutes')
        LOGGER.debug('Setting refresh rate to %s minutes', refresh_rate_in_minutes)
        USER_CONFIGURATION.set_refresh_time_seconds(refresh_rate_as_seconds)

def show_current_notification_url():
    """ Print out the current notification url """
    url = USER_CONFIGURATION.get_notification_subscription_url()
    if url:
        print(f'Notification URL {url}')
    else:
        print('No notification url has been set.')

def get_seconds_from_minutes(minutes: int) -> int:
    """ Simple utility to convert minutes into seconds """
    return minutes * 60

def get_minutes_from_seconds(seconds: int) -> int:
    """ Simple Utility to convert seconds into minutes """
    return seconds / 60

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
    parser.add_argument("-nu", "--notifications-url", help="View the notifications url", action="store_true")
    parser.add_argument("-cn", "--clear-notifications", help="Clears all notifications from the local history", action="store_true")
    parser.add_argument("-r", "--refresh-rate", help="Set/View the refresh rate in minutes", nargs="?", const=-1, type=int)
    args = parser.parse_args()

    loglevel = 'WARN'
    configure_notifications = False
    dump_notifications = False
    send_test_notification = False
    delete_all_notifications = False
    show_notification_url = False
    set_refresh_rate = False
    view_refresh_rate = False
    refresh_rate_as_seconds = UserConfiguration.DEFAULT_SLEEP_TIME_SECONDS
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
    elif args.notifications_url:
        show_notification_url = True
    elif args.refresh_rate:
        input_rate_as_seconds = get_seconds_from_minutes(args.refresh_rate)
        if input_rate_as_seconds < UserConfiguration.DEFAULT_SLEEP_TIME_SECONDS:
            view_refresh_rate = True
        else:
            set_refresh_rate = True
            refresh_rate_as_seconds = input_rate_as_seconds

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
    elif view_refresh_rate:
        view_current_refresh_rate()
    elif set_refresh_rate:
        set_new_refresh_rate(refresh_rate_as_seconds)
    elif show_notification_url:
        show_current_notification_url()
    else:
        run_slot_check()

if __name__ == "__main__":
    main(sys.argv[1:])
