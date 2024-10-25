import unittest
from unittest.mock import patch, MagicMock
import subprocess
from vpn_manager import disconnect,connect,is_nordvpn_running


class TestVPNFunctions(unittest.TestCase):

    @patch('subprocess.run')
    def test_disconnect_success(self, mock_run):
        disconnect()
        mock_run.assert_called_once_with('nordvpn -d', shell=True, check=True, cwd=r"C:\Program Files\NordVPN")

    @patch('subprocess.run')
    def test_connect_success(self, mock_run):
        connect()
        mock_run.assert_called_once_with('nordvpn -c -g "United States"', shell=True, check=True,
                                         cwd=r"C:\Program Files\NordVPN")

    @patch('subprocess.run')
    def test_disconnect_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'nordvpn -d')
        disconnect()  # Should not raise an error

    @patch('subprocess.run')
    def test_connect_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'nordvpn -c -g "United States"')
        connect()  # Should not raise an error

    @patch('psutil.process_iter')
    def test_is_nordvpn_running_true(self, mock_process_iter):
        mock_process = MagicMock()
        mock_process.info = {'pid': 1234, 'name': 'NordVPN.exe'}
        mock_process_iter.return_value = [mock_process]

        self.assertTrue(is_nordvpn_running())

    @patch('psutil.process_iter')
    def test_is_nordvpn_running_false(self, mock_process_iter):
        mock_process_iter.return_value = []  # No processes

        self.assertFalse(is_nordvpn_running())


if __name__ == '__main__':
    unittest.main()