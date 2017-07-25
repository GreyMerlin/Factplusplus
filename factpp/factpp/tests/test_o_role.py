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
    Test creating sub-property of an object property.
    """
    reasoner = Reasoner()

    r = reasoner.object_role('R')
    sub_r = reasoner.object_role('SR')
    reasoner.implies_o_roles(sub_r, r)
    assert reasoner.is_sub_o_role(sub_r, r)

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

def test_get_o_domain_range():
    """
    Test getting object role domain and range.
    """
    reasoner = Reasoner()

    r = reasoner.object_role('R')

    c1 = reasoner.concept('C1')
    reasoner.set_o_domain(r, c1)
    c2 = reasoner.concept('C2')
    reasoner.set_o_range(r, c2)

    values = reasoner.get_o_domain(r)
    assert 'C1' == next(values).name
    assert next(values, None) is None

    values = reasoner.get_o_range(r)
    assert 'C2' == next(values).name
    assert next(values, None) is None

def test_inverse_role():
    """
    Test getting inverse of an object role.
    """
    reasoner = Reasoner()

    r = reasoner.object_role('R')

    i1 = reasoner.individual('A1')
    i2 = reasoner.individual('A2')
    i3 = reasoner.individual('B')
    # ([A1, A2], R, B)
    reasoner.related_to(i1, r, i3)
    reasoner.related_to(i2, r, i3)

    r_inv = reasoner.inverse(r)
    values = reasoner.get_role_fillers(i3, r_inv)
    assert ['A1', 'A2'] == [i.name for i in values]

def test_set_inverse_role():
    """
    Test setting two object roles as inverse.
    """
    reasoner = Reasoner()

    r = reasoner.object_role('R1')
    r_inv = reasoner.object_role('R2')

    i1 = reasoner.individual('A1')
    i2 = reasoner.individual('A2')
    i3 = reasoner.individual('B')
    # ([A1, A2], R, B)
    reasoner.related_to(i1, r, i3)
    reasoner.related_to(i2, r, i3)

    reasoner.set_inverse_roles(r, r_inv)

    values = reasoner.get_role_fillers(i3, r_inv)
    assert ['A1', 'A2'] == [i.name for i in values]

# vim: sw=4:et:ai
