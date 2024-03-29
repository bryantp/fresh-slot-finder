"""
    Module for slot finding related classes and functions
"""
from abc import ABC
import os
import time
import datetime
import platform
from typing import List
import logging


from selenium import webdriver
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)

class NotLoggedInError(Exception):
    """ Error for a user who has not gone through the login flow """

    def __init__(self, message):
        super().__init__()
        self.message = message

class AmazonSlotFinder(ABC):
    """ Responsible for finding the available slots in an Amazon Fresh order """

    DATE_FORMAT_STRING = "%Y-%m-%d"
    DRIVER_PATH = './drivers/'
    #pylint:disable-msg=C0301
    LOGIN_QUERY = 'Please login to Amazon, navigate to the timeslot selection page and press enter to continue'

    def __init__(self, driver):
        #pylint:disable-msg=C0301
        self.url = 'https://www.amazon.com/gp/buy/shipoptionselect/handlers/display.html?hasWorkingJavascript=1'
        self.driver = driver
        self.parsed_source = ''
        self.logged_in = False # A default assumption that the user will not be logged in
        super().__init__()

    def get_driver_for_browser_and_os(self, browser: str) -> str:
        """
            Returns the proper driver file for the given browser and operating system
        """
        for entry in os.scandir(self.DRIVER_PATH):
            if (entry.name.startswith(browser) and
                    entry.name.endswith(AmazonSlotFinder._get_os_exec_extension())):
                return entry.path
        raise FileNotFoundError(f'Could not find a browser driver for {browser} and the current os')

    @staticmethod
    def _get_os_exec_extension() -> str:
        current_system = platform.system()
        # I am using my own extension for Mac and Linux as the filenames are the same.
        if current_system == 'Windows':
            return '.exe'
        if current_system == 'Darwin':
            return '.mac'
        if current_system == 'Linux':
            return '.linux'
        return ''

    def login(self):
        """
            Opens the web page and wait for the user to login.
            Sets up the webpage so that the correct page is open in the browser instance
        """
        self.driver.get(self.url)
        time.sleep(2)
        input(self.LOGIN_QUERY)
        self.logged_in = True

    def get_date_range(self) -> List[str]:
        """
            Return the list of date range string in the format that Amazon has in its data attributes: 2020-04-02
        """
        results = []
        current_date_time = datetime.date.today()
        results.append(current_date_time.strftime(self.DATE_FORMAT_STRING))
        for i in range(1, 8):
            date_time_step = current_date_time + datetime.timedelta(days=i)
            results.append(date_time_step.strftime(self.DATE_FORMAT_STRING))
        return results

    @staticmethod
    def has_open_slots(time_slot, date: str) -> bool:
        """
            Determines if there are any open times slots for amazon fresh delivery.

            It checks to see if there is an alert on the page telling the user that nothing is available.
            It no alert is found, then it looks for the radio buttons that are presented to the user and checks to see if they are disabled.
            If the number of radio buttons (dates) found is equal to the number of disabled radio buttons, then there are no dates available.
        """
        LOGGER.debug('Checking for time slot for date %s', date)
        if time_slot is None:
            LOGGER.debug('No Time Slot found for %s', date)
            return False
        # We're going to retrieve the unattended time slots only for now. Quarantine yall
        time_slot_unattended = time_slot.find(
            "div", {"id": "slot-container-UNATTENDED"})

        if time_slot_unattended.find("div", {"class": "a-box a-alert a-alert-info"}):
            # There is an alert box telling us that there is no time slot available for the given date
            LOGGER.debug('No available dates for %s', date)
            return False

        list_of_time_slots = time_slot_unattended.find(
            "div", {"id": f'root-{date}-UNATTENDED-box-group'}).find_all("div", recursive=False)

        list_of_disabled_time_slots = time_slot_unattended.find(
            "div", {"id": f'root-{date}-UNATTENDED-box-group'}).find_all("div", {"class": "disabledRadioBox"})

        LOGGER.debug('Number of time slots found: %s ', len(list_of_time_slots))
        LOGGER.debug(
            'Number of disabled time slots found: %s', len(list_of_disabled_time_slots))
        return len(list_of_time_slots) != len(list_of_disabled_time_slots)

    def refresh_page(self):
        """ Refreshes the current page """
        self.driver.refresh()
        LOGGER.debug('Sleeping the thread after refresh')
        time.sleep(10) # There is no way to know when the async calls on the page are done.
        LOGGER.debug('Thread finished sleeping after refresh')

    def _parse_with_beautiful_soup(self):
        """
            Takes the source of the web page from selenium and parses it in a Beautiful Soup context
        """
        if not self.logged_in:
            raise NotLoggedInError('User must have gone through the logged in flow')
        source = self.driver.page_source
        self.parsed_source = BeautifulSoup(source, "html.parser")

    def _load_next_set_of_dates(self):
        """ Click the next button the page to load the next set of dates """
        next_button = self.driver.find_element_by_xpath("//*[@id='nextButton-announce']")
        if next_button:
            # Should now have loaded 8 dates
            LOGGER.debug('Clicking on the next button to load more dates')
            next_button.click()
            LOGGER.debug('Sleeping thread after clicking next')
            time.sleep(10)
            LOGGER.debug('Done sleeping after clicking next')

    def get_available_dates(self) -> List[str]:
        """
            Tries to find any dates that have open slots available for delivery
        """
        date_range = self.get_date_range()
        LOGGER.debug('Date Range - %s', date_range)

        self._load_next_set_of_dates()
        self._parse_with_beautiful_soup()

        available_dates = []
        for date in date_range:
            slot_container_id = f'slot-container-{date}'
            time_slot = self.parsed_source.find(id=slot_container_id)
            if AmazonSlotFinder.has_open_slots(time_slot, date):
                LOGGER.debug('Found an available time slot for %s', date)
                available_dates.append(date)
        return available_dates


class ChromeAmazonSlotFinder(AmazonSlotFinder):
    """
        Chrome specific slot finder
    """

    def __init__(self):
        driver_exec = self.get_driver_for_browser_and_os('chrome')
        driver = webdriver.Chrome(driver_exec)
        super().__init__(driver)
