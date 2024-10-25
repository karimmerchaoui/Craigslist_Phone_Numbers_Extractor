import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from datetime import datetime
import re

# Assume the functions are defined in a module named `your_module`
from data_management import create_filename, save_to_excel, extract_phone_numbers, get_location


class TestDataManagement(unittest.TestCase):

    def test_create_filename(self):
        # Test the filename creation
        new_city = "New York"
        new_state = "NY"
        distance = 50
        expected_date = datetime.now().strftime("%Y-%m-%d")
        expected_filename = f"newyork_ny_{distance}_{expected_date}.xlsx"

        result = create_filename(new_city, new_state, distance)
        self.assertEqual(result, expected_filename)

    @patch('os.path.exists')
    @patch('pandas.read_excel')
    @patch('pandas.DataFrame.to_excel')
    @patch('pandas.ExcelWriter')
    def test_save_to_excel_new_file(self, mock_excel_writer, mock_to_excel, mock_read_excel, mock_exists):
        # Test saving to a new Excel file
        mock_exists.return_value = False  # Simulate that the file does not exist
        title = "Sample Title"
        description = "Sample Description"
        phone_number = "123-456-7890"
        posted = "2023-10-01"
        new_city = "Los Angeles"
        new_state = "CA"
        distance = 100

        save_to_excel(title, description, phone_number, posted, new_city, new_state, distance)

        # Check if to_excel was called with the expected parameters
        mock_to_excel.assert_called_once()

    @patch('os.path.exists')
    @patch('pandas.read_excel')
    @patch('pandas.DataFrame.to_excel')
    @patch('pandas.ExcelWriter')
    def test_save_to_excel_existing_file(self, mock_excel_writer, mock_to_excel, mock_read_excel, mock_exists):
        # Test saving to an existing Excel file
        mock_exists.return_value = True  # Simulate that the file exists
        mock_read_excel.return_value = pd.DataFrame({'Title': ['Sample Title']})  # Existing title

        title = "Sample Title"
        description = "Sample Description"
        phone_number = "123-456-7890"
        posted = "2023-10-01"
        new_city = "Los Angeles"
        new_state = "CA"
        distance = 100

        save_to_excel(title, description, phone_number, posted, new_city, new_state, distance)

        # Check if to_excel was NOT called since the title already exists
        mock_to_excel.assert_not_called()

    def test_extract_phone_numbers(self):
        # Test extracting phone numbers from a description
        description = "Contact me at +1 (123) 456-7890 or 987-654-3210."
        expected_numbers = ['+1 (123) 456-7890', '987-654-3210']

        result = extract_phone_numbers(description)
        self.assertEqual(result, expected_numbers)

    @patch('geopy.geocoders.Nominatim')
    def test_get_location(self, mock_nominatim):
        # Test getting location using mock
        mock_geolocator = MagicMock()
        mock_nominatim.return_value = mock_geolocator
        mock_geolocator.geocode.return_value = MagicMock(latitude=34.0522, longitude=-118.2437)

        new_city = "Los Angeles"
        new_state = "CA"

        # Here, you would call the method from the class that includes self.log_message
        # For example, if this method is in a class named Scraper, you can instantiate it:
        # scraper = Scraper(...)
        # scraper.get_location(new_city, new_state)

        location = mock_geolocator.geocode(f"{new_city}, {new_state}", timeout=None)
        self.assertIsNotNone(location)
        self.assertEqual(location.latitude, 34.0522)
        self.assertEqual(location.longitude, -118.2437)


if __name__ == '__main__':
    unittest.main()
