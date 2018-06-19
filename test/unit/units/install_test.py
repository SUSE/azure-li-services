from pytest import raises
from unittest.mock import (
    patch, call, Mock
)
from azure_li_services.units.install import main
from azure_li_services.exceptions import AzureHostedInstallException


class TestInstall(object):
    @patch('azure_li_services.command.Command.run')
    @patch('azure_li_services.units.install.Defaults.get_config_file')
    @patch('azure_li_services.units.install.Path.create')
    @patch('azure_li_services.units.install.glob.iglob')
    @patch('azure_li_services.units.install.StatusReport')
    @patch('azure_li_services.defaults.Defaults.mount_config_source')
    def test_main(
        self, mock_mount_config_source, mock_StatusReport, mock_iglob,
        mock_Path_create, mock_get_config_file, mock_Command_run
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        command_result = Mock()
        command_result.output = 'foo'
        mock_Command_run.return_value = command_result
        mock_iglob.return_value = ['/var/lib/localrepos/azure_packages/foo.rpm']
        mock_get_config_file.return_value = '../data/config.yaml'
        main()
        mock_StatusReport.assert_called_once_with('install')
        status.set_success.assert_called_once_with()
        mock_Path_create.assert_called_once_with(
            '/var/lib/localrepos/azure_packages'
        )
        assert mock_Command_run.call_args_list == [
            call(
                [
                    'bash', '-c', 'rsync -zav {0}/directory-with-rpm-files/* '
                    '{0}/another-directory-with-rpm-files/* '
                    '/var/lib/localrepos/azure_packages'.format(
                        mock_mount_config_source.return_value.location
                    )
                ]
            ),
            call(['createrepo', '/var/lib/localrepos/azure_packages']),
            call(
                ['zypper', 'removerepo', 'azure_packages'],
                raise_on_error=False
            ),
            call(
                [
                    'zypper', 'addrepo', '--no-gpgcheck',
                    '/var/lib/localrepos/azure_packages', 'azure_packages'
                ]
            ),
            call(
                [
                    'rpm', '-qp', '--qf', '%{NAME}',
                    '/var/lib/localrepos/azure_packages/foo.rpm'
                ]
            ),
            call(
                [
                    'zypper', '--non-interactive', 'install',
                    '--auto-agree-with-licenses', 'foo'
                ]
            ),
            call(['umount', mock_mount_config_source.return_value.location])
        ]

    @patch('azure_li_services.units.install.Defaults.get_config_file')
    @patch('azure_li_services.units.install.RuntimeConfig')
    @patch('azure_li_services.units.install.StatusReport')
    def test_main_raises(
        self, mock_StatusReport, mock_RuntimeConfig, mock_get_config_file
    ):
        config = Mock()
        mock_RuntimeConfig.return_value = config
        config.get_packages_config.return_value = {'packages': None}
        with raises(AzureHostedInstallException):
            main()
