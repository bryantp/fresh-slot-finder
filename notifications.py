"""
    Handles interacting with the notification service
"""
import logging

from notify_run import Notify

from database import UserConfiguration

class NotificationService:
    """ Send notifications and handles retrieving service urls """

    LOGGER = logging.getLogger(__name__)

    def __init__(self, endpoint_url: str):
        self.notify = Notify(endpoint=endpoint_url)
        self.user_configuration = UserConfiguration()

    def send(self, notification: str):
        """ Send a notification to the service endpoint """
        self.LOGGER.debug(f'Sending Notification: {notification}')
        self.notify.send(notification)
        self.user_configuration.insert_notification_history(notification)

    @staticmethod
    def get_new_subscription_url():
        """ Retrieve a new subscrption url from the remote service """
        service_url = Notify().register().endpoint
        NotificationService.LOGGER.debug(f'Retrieved new service URL: {service_url}')
        return service_url
