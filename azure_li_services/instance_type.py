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
from collections import namedtuple


class InstanceType(object):
    Constants = namedtuple(
        'Constants', ['li', 'vli', 'vli_gen3']
    )
    constants = Constants('li', 'vli', 'vli_gen3')

    li = constants.li
    vli = constants.vli
    vli_gen3 = constants.vli_gen3
