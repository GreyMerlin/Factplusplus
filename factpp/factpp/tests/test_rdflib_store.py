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
RDFLib store unit tests.
"""

from rdflib import Graph, Literal, BNode
from rdflib.namespace import FOAF, RDF, RDFS, OWL, Namespace

import factpp.rdflib
from .._factpp import Reasoner

from unittest import mock

NS = Namespace('http://test.com/ns#')

class MockProxy:
    def __init__(self, reasoner, method):
        self.reasoner = reasoner
        self.method = method
        self.mock = mock.MagicMock()

    def __getattr__(self, attr):
        if attr == self.method:
            return self.mock
        else:
            return getattr(self.reasoner, attr)

def graph(mock=None):
    store = factpp.rdflib.Store()
    if mock:
        store._reasoner = MockProxy(store._reasoner, mock)
        # reset parsers after mock is created
        store._create_parsers()
    g = Graph(store=store)
    return g, g.store._reasoner

def test_property_domain():
    g, reasoner = graph()

    g.add((FOAF.knows, RDF.type, OWL.ObjectProperty))
    g.add((FOAF.knows, RDFS.domain, FOAF.Person))

    r = reasoner.object_role(str(FOAF.knows))
    value = next(reasoner.get_o_domain(r))
    assert value.name == str(FOAF.Person)

def test_property_range():
    g, reasoner = graph()

    g.add((FOAF.knows, RDF.type, OWL.ObjectProperty))
    g.add((FOAF.knows, RDFS.range, FOAF.Person))

    r = reasoner.object_role(str(FOAF.knows))
    value = next(reasoner.get_o_range(r))
    assert value.name == str(FOAF.Person)

def test_class_instance():
    g, reasoner = graph()

    p = BNode()
    cls = reasoner.concept(str(FOAF.Person))
    obj = reasoner.individual(str(p))

    g.add((p, RDF.type, FOAF.Person))

    assert reasoner.is_instance(obj, cls)

def test_subclass_of():
    g, reasoner = graph()

    g.add((NS.Woman, RDFS.subClassOf, NS.Person))

    cls_w = reasoner.concept(str(NS.Woman))
    cls_p = reasoner.concept(str(NS.Person))
    assert reasoner.is_subsumed_by(cls_w, cls_p)

def test_owl_intersection_subclass():
    g, reasoner = graph()

    p = BNode('John')
    g.add((p, RDF.type, NS.Grandfather))

    b1 = BNode()
    b2 = BNode()

    g.add((NS.Grandfather, RDFS.subClassOf, b1))
    g.add((b1, OWL.intersectionOf, b2))
    g.add((b2, RDF.first, NS.Parent))
    g.add((b2, RDF.rest, NS.Man))

    i = reasoner.individual(str(p))
    cls_p = reasoner.concept(str(NS.Parent))
    cls_m = reasoner.concept(str(NS.Man))
    assert reasoner.is_instance(i, cls_p)
    assert reasoner.is_instance(i, cls_m)

def test_owl_intersection_eq_class():
    g, reasoner = graph()

    p = BNode('Alice')
    g.add((p, RDF.type, NS.Parent))
    g.add((p, RDF.type, NS.Woman))

    b1 = BNode()
    b2 = BNode()

    g.add((NS.Mother, OWL.equivalentClass, b1))
    g.add((b1, OWL.intersectionOf, b2))
    g.add((b2, RDF.first, NS.Parent))
    g.add((b2, RDF.rest, NS.Woman))

    i = reasoner.individual(str(p))
    cls_m = reasoner.concept(str(NS.Mother))
    assert reasoner.is_instance(i, cls_m)

def test_new_class():
    """
    Test adding new classes.
    """
    g, reasoner = graph()
    parsers = g.store._parsers

    g.add((NS.A, RDF.type, OWL.Class))
    g.add((NS.B, RDF.type, RDFS.Class))
    assert (RDF.type, NS.A) in parsers
    assert (RDF.type, NS.B) in parsers

def test_new_o_property():
    """
    Test adding new object property.
    """
    g, reasoner = graph()
    parsers = g.store._parsers

    g.add((NS.P, RDF.type, OWL.ObjectProperty))
    assert NS.P in parsers
    assert (NS.P, RDFS.domain) in parsers
    assert (NS.P, RDFS.range) in parsers

def test_new_d_property():
    """
    Test adding new data property.
    """
    g, reasoner = graph()
    parsers = g.store._parsers

    g.add((NS.P, RDF.type, OWL.DatatypeProperty))
    assert (NS.P, RDFS.domain) in parsers
    assert (NS.P, RDFS.range) in parsers

def test_d_property_range():
    """
    Test setting data property range.
    """
    g, reasoner = graph()
    parsers = g.store._parsers

    g.add((NS.P, RDF.type, OWL.DatatypeProperty))
    g.add((NS.P, RDFS.range, RDFS.Literal))

    assert NS.P in parsers

def test_d_property_set_str():
    """
    Test setting data property string value.
    """
    g, reasoner = graph('value_of_str')

    g.add((NS.P, RDF.type, OWL.DatatypeProperty))
    g.add((NS.P, RDFS.range, RDFS.Literal))
    g.add((NS.O, NS.P, Literal('a-value')))

    i = reasoner.individual(str(NS.O))
    r = reasoner.data_role(str(NS.P))
    reasoner.value_of_str.assert_called_once_with(i, r, 'a-value')

def test_equivalent_classes():
    """
    Test equivalent classes.
    """
    g, reasoner = graph('equal_concepts')

    g.add((NS.P1, OWL.equivalentClass, NS.P2))

    c1 = reasoner.concept(str(NS.P1))
    c2 = reasoner.concept(str(NS.P2))
    reasoner.equal_concepts.assert_called_once_with([c1, c2])

def test_disjoin_with():
    """
    Test disjoint classes.
    """
    g, reasoner = graph('disjoint_concepts')

    g.add((NS.P1, OWL.disjointWith, NS.P2))

    c1 = reasoner.concept(str(NS.P1))
    c2 = reasoner.concept(str(NS.P2))
    reasoner.disjoint_concepts.assert_called_once_with([c1, c2])

def test_inverse_role():
    """
    Test setting OWL invverse role.
    """
    g, reasoner = graph()

    g, reasoner = graph()
    g.add((NS.P1, RDF.type, OWL.ObjectProperty))
    g.add((NS.P2, RDF.type, OWL.ObjectProperty))
    g.add((NS.P2, OWL.inverseOf, NS.P1))

    g.add((NS.C, RDF.type, OWL.Class))
    g.add((NS.A1, RDF.type, NS.C))
    g.add((NS.A2, RDF.type, NS.C))
    g.add((NS.B, RDF.type, NS.C))

    g.add((NS.A1, NS.P1, NS.B))
    g.add((NS.A2, NS.P1, NS.B))

    r_inv = reasoner.object_role(str(NS.P2))
    i = reasoner.individual(str(NS.B))
    values = reasoner.get_role_fillers(i, r_inv)
    assert [str(NS.A1), str(NS.A2)] == [i.name for i in values]

def test_list_cache():
    """
    Test creating RDF list state.
    """
    cache = factpp.rdflib.ListState.CACHE
    store = mock.Mock()

    cache['O1'].store = store
    cache['O1'].object = 'O1'

    cache['O1'].subject = 'S'
    assert 0 == store._reasoner.concept.call_count

    cache['O1'].first = 'F'
    assert 0 == store._reasoner.concept.call_count

    cache['O1'].rest = 'R'
    assert 3 == store._reasoner.concept.call_count

    assert 'O1' not in cache

    # in different order
    store.reset_mock()
    cache['O2'].store = store
    cache['O2'].object = 'O2'

    cache['O2'].rest = 'R'
    assert 0 == store._reasoner.concept.call_count

    cache['O2'].first = 'F'
    assert 0 == store._reasoner.concept.call_count

    cache['O2'].subject = 'S'
    assert 3 == store._reasoner.concept.call_count

    assert 'O2' not in cache

# vim: sw=4:et:ai
