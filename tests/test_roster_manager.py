# tests/test_roster_manager.py

import sys
import os

import unittest
from unittest.mock import patch, mock_open
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils.roster_manager as roster_manager # Import the module that contains the function to test

class TestRosterManager(unittest.TestCase):
    @patch('utils.roster_manager.gspread')
    @patch('utils.roster_manager.Credentials')
    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        'settings': {
            '2024': {
                'roster_google_sheet_name': '2024_Rosters'
            }
        }
    }))
    def test_access_sheet_in_drive(self, mock_open, mock_credentials, mock_gspread):
        # Set up the mocks
        mock_credentials.from_service_account_file.return_value = 'test credentials'
        mock_gspread.service_account.return_value.open.return_value.get_worksheet.return_value = 'test worksheet'

        # Call the function to test
        worksheet = roster_manager.access_sheet_in_drive()

        # Check that the function called the mocks correctly
        mock_open.assert_called_once_with('yearly_settings.json', 'r')
        mock_credentials.from_service_account_file.assert_called_once_with('credentials.json')
        mock_gspread.service_account.assert_called_once_with(credentials='test credentials')
        mock_gspread.service_account.return_value.open.assert_called_once_with('Test Sheet')
        mock_gspread.service_account.return_value.open.return_value.get_worksheet.assert_called_once_with(0)

        # Check that the function returned the correct result
        self.assertEqual(worksheet, 'test worksheet')

if __name__ == '__main__':
    unittest.main()