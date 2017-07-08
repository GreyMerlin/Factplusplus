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

def test_get_o_domain():
    """
    Test getting object role domain.
    """
    reasoner = Reasoner()

    cls = reasoner.concept('CLS')
    r = reasoner.object_role('R')
    reasoner.set_o_domain(r, cls)

    values = reasoner.get_o_domain(r)
    assert 'CLS' == next(values).name
    assert next(values, None) is None

def test_get_o_range():
    """
    Test getting object role range.
    """
    reasoner = Reasoner()

    cls = reasoner.concept('CLS')
    r = reasoner.object_role('R')
    reasoner.set_o_range(r, cls)

    values = reasoner.get_o_range(r)
    assert 'CLS' == next(values).name
    assert next(values, None) is None


# vim: sw=4:et:ai
