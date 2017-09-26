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

"""
Unit tests for property parser used by RDFLib store.
"""

from factpp.rdflib import PropertyParser

from unittest import mock

def _parser():
    return PropertyParser(mock.MagicMock())

def test_cache_parse_range():
    """
    Test parser cache for property range.
    """
    parser = _parser()
    o = mock.MagicMock()

    parser.parse_range(o)

    assert ('parse_range', o) in parser._cache

def test_set_role_object_property():
    """
    Test property parser for an object property.
    """
    parser = _parser()

    role = mock.MagicMock()
    parser.set_role('object', role)

    assert parser._type == 'object'
    assert parser._role is role
    assert parser.parse_range == parser._object_parse_range

def test_set_role_data_property():
    """
    Test property parser for a data property.
    """
    parser = _parser()

    role = mock.MagicMock()
    parser.set_role('data', role)

    assert parser._type == 'data'
    assert parser._role is role
    assert parser.parse_range == parser._data_parse_range

# vim: sw=4:et:ai
