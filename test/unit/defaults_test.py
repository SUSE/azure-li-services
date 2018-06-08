from unittest.mock import patch
from pytest import raises

from azure_li_services.defaults import Defaults
from azure_li_services.exceptions import AzureHostedConfigFileNotFoundException


class TestDefaults(object):
    @patch('os.path.exists')
    def test_get_config_file(self, mock_os_path_exists):
        mock_os_path_exists.return_value = True
        assert Defaults.get_config_file() == '/etc/suse_firstboot_config.yaml'
        mock_os_path_exists.return_value = False
        with raises(AzureHostedConfigFileNotFoundException):
            Defaults.get_config_file()

    def test_get_status_report_directory(self):
        assert Defaults.get_status_report_directory() == \
            '/var/lib/azure_li_services'
