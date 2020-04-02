"""
    Main Program Entry Point
"""

from slot_finder import ChromeAmazonSlotFinder

parser = ChromeAmazonSlotFinder()
parser.login()
parser.parse_with_beautiful_soup()
parser.get_available_dates()