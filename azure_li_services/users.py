# Copyright (c) 2018 SUSE Linux GmbH.  All rights reserved.
#
# This file is part of azure-li-services.
#
# azure-li-services is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# azure-li-services is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with azure-li-services.  If not, see <http://www.gnu.org/licenses/>
#
from azure_li_services.command import Command


class Users(object):
    """
    Operations on users and groups
    """
    def user_exists(self, user_name):
        """
        Check if user exists

        :param str user_name: user name

        :rtype: bool
        """
        return self._search_for(user_name, '/etc/passwd')

    def group_exists(self, group_name):
        """
        Check if group exists

        :param str group_name: group name

        :return: True or False

        :rtype: bool
        """
        return self._search_for(group_name, '/etc/group')

    def group_add(self, group_name, options):
        """
        Add group with options

        :param str group_name: group name
        :param list options: groupadd options
        """
        Command.run(
            ['groupadd'] + options + [group_name]
        )

    def user_add(self, user_name, options):
        """
        Add user with options

        :param str user_name: user name
        :param list options: useradd options
        """
        Command.run(
            ['useradd'] + options + [user_name]
        )

    def user_modify(self, user_name, options):
        """
        Modify user with options

        :param str user_name: user name
        :param list options: usermod options
        """
        Command.run(
            ['usermod'] + options + [user_name]
        )

    def setup_change_password_on_logon(self, user_name):
        """
        Setup when a user must change his/her password.

        The method sets the number of days when the password was
        last changed to zero. This causes a must change password
        request on next login

        :param str user_name: user name
        """
        Command.run(
            ['chage', '-d', '0', user_name]
        )

    def setup_home_for_user(self, user_name, group_name, home_path):
        """
        Setup user home directory

        :param str user_name: user name
        :param str group_name: group name
        :param str home_path: path name
        """
        user_and_group = user_name + ':' + group_name
        Command.run(
            ['chown', '-R', user_and_group, home_path]
        )

    def _search_for(self, name, in_file):
        search = '^' + name + ':'
        try:
            Command.run(
                ['grep', '-q', search, in_file]
            )
        except Exception:
            return False
        return True
