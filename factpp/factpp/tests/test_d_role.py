#
# factpp - Python interface to FaCT++ reasoner
#
# Copyright (C) 2016-2017 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from .._factpp import Reasoner

def test_sub_property():
    """
    Test creating sub-property of a data property.
    """
    reasoner = Reasoner()

    r = reasoner.data_role('R')
    sub_r = reasoner.data_role('SR')
    reasoner.implies_d_roles(sub_r, r)
    assert reasoner.is_sub_d_role(sub_r, r)

# vim: sw=4:et:ai
