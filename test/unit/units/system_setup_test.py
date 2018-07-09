import io
import os
from textwrap import dedent
from unittest.mock import (
    patch, Mock, MagicMock, call
)
from azure_li_services.runtime_config import RuntimeConfig
from azure_li_services.units.system_setup import main

import azure_li_services.units.system_setup as system_setup


class TestSystemSetup(object):
    def setup(self):
        self.config = RuntimeConfig('../data/config.yaml')

    @patch.object(system_setup, 'set_hostname')
    @patch.object(system_setup, 'set_kdump_service')
    @patch.object(system_setup, 'set_kernel_samepage_merging_mode')
    @patch.object(system_setup, 'set_energy_performance_settings')
    @patch.object(system_setup.Defaults, 'get_config_file')
    @patch.object(system_setup, 'RuntimeConfig')
    @patch.object(system_setup, 'StatusReport')
    def test_main(
        self, mock_StatusReport, mock_RuntimConfig, mock_get_config_file,
        mock_set_energy_performance_settings,
        mock_set_kernel_samepage_merging_mode,
        mock_set_kdump_service, mock_set_hostname
    ):
        status = Mock()
        mock_StatusReport.return_value = status
        mock_RuntimConfig.return_value = self.config
        main()
        mock_set_hostname.assert_called_once_with('azure')
        mock_set_kdump_service.assert_called_once_with(160, 80)
        mock_set_kernel_samepage_merging_mode.assert_called_once_with()
        mock_set_energy_performance_settings.assert_called_once_with()
        mock_StatusReport.assert_called_once_with('system_setup')
        status.set_success.assert_called_once_with()

    @patch('azure_li_services.command.Command.run')
    def test_set_hostname(self, mock_Command_run):
        system_setup.set_hostname('azure')
        mock_Command_run.assert_called_once_with(
            ['hostnamectl', 'set-hostname', 'azure']
        )

    @patch('os.chmod')
    def test_set_kernel_samepage_merging_mode(self, mock_os_chmod):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            system_setup.set_kernel_samepage_merging_mode()
            assert mock_open.call_args_list == [
                call('/sys/kernel/mm/ksm/run', 'w'),
                call('/etc/init.d/boot.local', 'a')
            ]
            assert file_handle.write.call_args_list == [
                call('0\n'),
                call('echo 0 > /sys/kernel/mm/ksm/run\n'),
            ]
            mock_os_chmod.assert_called_once_with(
                '/etc/init.d/boot.local', 0o755
            )

    @patch('os.chmod')
    @patch('azure_li_services.command.Command.run')
    def test_set_energy_performance_settings(
        self, mock_Command_run, mock_os_chmod
    ):
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            system_setup.set_energy_performance_settings()
            mock_open.assert_called_once_with(
                '/etc/init.d/boot.local', 'a'
            )
            assert file_handle.write.call_args_list == [
                call('cpupower frequency-set -g performance\n'),
                call('cpupower set -b 0\n')
            ]
            assert mock_Command_run.call_args_list == [
                call(['cpupower', 'frequency-set', '-g', 'performance']),
                call(['cpupower', 'set', '-b', '0'])
            ]
            mock_os_chmod.assert_called_once_with(
                '/etc/init.d/boot.local', 0o755
            )

    @patch('azure_li_services.command.Command.run')
    def test_set_kdump_service(self, mock_Command_run):
        kdumptool_call = Mock()
        kdumptool_call.output = dedent('''
            Total: 16308
            Low: 72
            High: 123
            MinLow: 72
            MaxLow: 2455
            MinHigh: 0
            MaxHigh: 13824
        ''').strip() + os.linesep
        mock_Command_run.return_value = kdumptool_call
        system_setup.set_kdump_service(None, None)
        assert mock_Command_run.call_args_list == [
            call(['kdumptool', 'calibrate']),
            call(
                [
                    'sed', '-ie',
                    's@crashkernel=[0-9]\\+M,low@crashkernel=72M,low@',
                    '/etc/default/grub'
                ]
            ),
            call(
                [
                    'sed', '-ie',
                    's@crashkernel=[0-9]\\+M,high@crashkernel=123M,high@',
                    '/etc/default/grub'
                ]
            ),
            call(['grub2-mkconfig', '-o', '/boot/grub2/grub.cfg']),
            call(['systemctl', 'restart', 'kdump'])
        ]
