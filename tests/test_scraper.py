import unittest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


# Assuming the Scraper class is in a module named scraper_module
# from scraper_module import Scraper

class Scraper:
    def __init__(self, update_progress_callback, update_state_callback, log_message):
        self.update_progress = update_progress_callback
        self.update_state = update_state_callback
        self.log_message = log_message

    def get_posts(self, soup1):
        links = []
        l = len(soup1)
        for j, i in enumerate(soup1):
            self.update_progress(int((j / l) * 100))
            a = i.find('a')
            h = a.get('href')
            try:
                resume_page = requests.get(h, timeout=10)
                soup2 = BeautifulSoup(resume_page.text, "html.parser")
                posting_body_a = soup2.select_one("#postingbody a")
                if posting_body_a and posting_body_a.get('href') == '#':
                    links.append(h)
            except requests.exceptions.RequestException as e:
                self.log_message(f"Error accessing {h}: {e}")
        return links

    def get_location(self, new_city, new_state):
        geolocator = Nominatim(user_agent="my-app")
        location = geolocator.geocode(f"{new_city}, {new_state}", timeout=None)
        if not location:
            self.log_message("City not found")
            return


class TestScraper(unittest.TestCase):

    @patch('requests.get')
    @patch('bs4.BeautifulSoup')
    @patch('geopy.geocoders.Nominatim.geocode')
    def test_get_location_success(self, mock_geocode):
        # Mock a successful geocode response
        mock_location = MagicMock()
        mock_location.latitude = 40.7128
        mock_location.longitude = -74.0060
        mock_geocode.return_value = mock_location

        log_message_mock = MagicMock()

        scraper = Scraper(lambda x: None, lambda x: None, log_message_mock)

        result = scraper.get_location("New York", "NY")

        self.assertIsNone(result)  # No return value expected on success

    @patch('geopy.geocoders.Nominatim.geocode')
    def test_get_location_failure(self, mock_geocode):
        # Mock a failed geocode response (city not found)
        mock_geocode.return_value = None

        log_message_mock = MagicMock()

        scraper = Scraper(lambda x: None, lambda x: None, log_message_mock)

        result = scraper.get_location("InvalidCity", "InvalidState")

        self.assertIsNone(result)  # No return value expected on failure
        log_message_mock.assert_called_once_with("City not found")


if __name__ == '__main__':
    unittest.main()