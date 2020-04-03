"""
    Handles all Database related operations
"""
from typing import Any
import os
import logging
import sqlite3
import yaml

from appdirs import AppDirs


class UserConfiguration:
    """
        Handle all persisted user information
    """

    DATABASE_NAME = 'slot_finder.db'
    CONFIG_FILE_NAME = 'slot_finder.yml'

    NOTIFICATION_CONFIG_SECTION = 'notifications'
    NOTIFICATION_SUB_KEY = 'subscription_url'

    LOGGER = logging.getLogger(__name__)

    CREATE_TABLE_NOTIFICATION_HISTORY = '''
        CREATE TABLE IF NOT EXISTS notification_history (id SERIAL PRIMARY KEY, sent_date_time TEXT, message TEXT)
    '''

    INSERT_NOTIFICATION_HISTORY = '''
        INSERT INTO notification_history (sent_date_time, message) VALUES (DateTime('now'),?)
    '''

    GET_N_LAST_NOTIFICATION_HISTORY = '''
        SELECT sent_date_time, message from notification_history ORDER BY sent_date_time DESC LIMIT ?
    '''

    CLEAR_NOTIFICATION_HISTORY_TABLE = '''
        DELETE FROM notification_history
    '''

    def __init__(self):
        self.dirs = AppDirs("SlotFinder", "Bryan")
        self.db_file = os.path.join(self.dirs.user_data_dir, self.DATABASE_NAME)
        self.config_file = os.path.join(self.dirs.user_config_dir, self.CONFIG_FILE_NAME)

    def _connect(self):
        """ Open the connection to the DB """
        return sqlite3.connect(self.db_file)

    def setup(self):
        """
            Handle DB creation if it does not exist
        """
        if not os.path.exists(self.dirs.user_data_dir):
            os.makedirs(self.dirs.user_data_dir)

        self.LOGGER.info('Connected to DB file at %s', self.db_file)
        connection = self._connect()

        cursor = connection.cursor()

        cursor.execute(self.CREATE_TABLE_NOTIFICATION_HISTORY)

        connection.commit()

        # Touch the file so we can make sure it exists
        with open(self.config_file, 'a'):
            pass

    def set_notification_subscription(self, url: str):
        """ Insert notification subscriptions into the DB """
        with open(self.config_file, 'w') as config:
            doc = {self.NOTIFICATION_CONFIG_SECTION: {self.NOTIFICATION_SUB_KEY: url}}
            yaml.dump(doc, config)

    def get_notification_subscription_url(self) -> Any:
        """
            Returns the notification subscription url that was generated before,
            or an empty string
        """
        with open(self.config_file, 'r') as config:
            config_file = yaml.load(config, Loader=yaml.FullLoader)

            if not config_file:
                self.LOGGER.info('No configuration file set')
                return ''

            if self.NOTIFICATION_CONFIG_SECTION not in config_file:
                self.LOGGER.warning('No notification url set in yaml file')
                return ''
            if self.NOTIFICATION_SUB_KEY not in config_file[self.NOTIFICATION_CONFIG_SECTION]:
                self.LOGGER.warning('No notification url set in yaml file')
                return ''

            return config_file[self.NOTIFICATION_CONFIG_SECTION][self.NOTIFICATION_SUB_KEY]

    def insert_notification_history(self, message: str):
        """ Insert notification history into the DB """
        connection = self._connect()
        cursor = connection.cursor()
        # YYYY-MM-DD HH:MM:SS.SSS
        cursor.execute(self.INSERT_NOTIFICATION_HISTORY, (message, ))
        connection.commit()
        connection.close()

    def get_all_n_notifications(self, limit: int) -> Any:
        """ Retrieve the last N notifications """
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(self.GET_N_LAST_NOTIFICATION_HISTORY, (limit,))
        notifications = cursor.fetchall()
        connection.close()
        return notifications

    def delete_all_notifications(self):
        """ Clears the notification history table """
        connection = self._connect()
        cursor = connection.cursor()
        cursor.execute(self.CLEAR_NOTIFICATION_HISTORY_TABLE)
        connection.commit()
        connection.close()
