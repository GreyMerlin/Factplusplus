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

from rdflib import Literal
from rdflib.namespace import FOAF, RDF, RDFS, OWL

from factpp.rdflib import PropertyParser

from .util import graph, NS
from unittest import mock

def _parser():
    return PropertyParser(mock.MagicMock())

def test_cache_parse_domain():
    """
    Test parser cache for property domain.
    """
    parser = _parser()
    s = mock.MagicMock()
    o = mock.MagicMock()

    parser.parse_domain(s, o)

    assert ('parse_domain', s, o) in parser._cache

def test_cache_parse_range():
    """
    Test parser cache for property range.
    """
    parser = _parser()
    s = mock.MagicMock()
    o = mock.MagicMock()

    parser.parse_range(s, o)

    assert ('parse_range', s, o) in parser._cache

def test_cache_parse_value():
    """
    Test parser cache for property value.
    """
    parser = _parser()
    s = mock.MagicMock()
    o = mock.MagicMock()

    parser.parse_value(s, o)

    assert ('parse_value', s, o) in parser._cache

def test_cache_parse_equivalent():
    """
    Test parser cache for equivalent properties.
    """
    parser = _parser()
    s = mock.MagicMock()
    o = mock.MagicMock()

    parser.parse_equivalent_property(s, o)

    assert ('parse_equivalent_property', s, o) in parser._cache

def test_cache_parse_functional():
    """
    Test parser cache for functional property.
    """
    parser = _parser()
    s = mock.MagicMock()
    o = mock.MagicMock()

    parser.parse_functional_property(s, o)

    assert ('parse_functional_property', s, o) in parser._cache

def test_cache_parse_inverse_functional():
    """
    Test parser cache for inverse_functional property.
    """
    parser = _parser()
    s = mock.MagicMock()
    o = mock.MagicMock()

    parser.parse_inverse_functional_property(s, o)

    assert ('parse_inverse_functional_property', s, o) in parser._cache

def test_set_role_object_property():
    """
    Test property parser for an object property.
    """
    parser = _parser()

    role = mock.MagicMock()
    parser.set_role('object', role)

    assert parser._type == 'object'
    assert parser._role is role
    assert parser.parse_domain == parser._object_parse_domain
    assert parser.parse_range == parser._object_parse_range
    assert parser.parse_value == parser._object_parse_value
    assert parser.parse_sub_property_of == parser._object_parse_sub_property_of
    assert parser.parse_equivalent_property == parser._object_parse_equivalent_property
    assert parser.parse_functional_property == parser._object_parse_functional_property
    assert parser.parse_inverse_functional_property == parser._object_parse_inverse_functional_property

def test_set_role_data_property():
    """
    Test property parser for a data property.
    """
    parser = _parser()

    role = mock.MagicMock()
    parser.set_role('data', role)

    assert parser._type == 'data'
    assert parser._role is role
    assert parser.parse_domain == parser._data_parse_domain
    assert parser.parse_range == parser._data_parse_range
    assert parser.parse_value == parser._data_parse_value
    assert parser.parse_sub_property_of == parser._data_parse_sub_property_of
    assert parser.parse_equivalent_property == parser._data_parse_equivalent_property
    assert parser.parse_functional_property == parser._data_parse_functional_property
    assert parser.parse_inverse_functional_property == parser._data_parse_inverse_functional_property

def test_delayed_property_type():
    """
    Test delayed assignment of property type.
    """
    g, reasoner = graph()

    # first, we have a property of unkown type (is it data or object
    # property?)
    g.add((NS.P, RDF.type, RDF.Property))
    g.add((NS.P, RDFS.domain, FOAF.Person))

    # set the property type
    g.add((NS.P, RDF.type, OWL.DatatypeProperty))

    # check the if the domain of the data property got set
    i = reasoner.individual(NS.O)
    r = reasoner.data_role(NS.P)
    value = next(reasoner.get_d_domain(r))
    assert value.name == str(FOAF.Person)

# vim: sw=4:et:ai
