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

from rdflib import BNode
from rdflib.namespace import RDF, RDFS, OWL

import factpp.rdflib

from .util import graph, NS

from unittest import mock

def test_class_instance():
    g, reasoner = graph()

    g.add((NS.C, RDF.type, OWL.Class))
    g.add((NS.A, RDF.type, NS.C))

    cls = reasoner.concept(NS.C)
    obj = reasoner.individual(NS.A)

    assert reasoner.is_instance(obj, cls)

def test_subclass_of():
    g, reasoner = graph()

    g.add((NS.Woman, RDFS.subClassOf, NS.Person))

    cls_w = reasoner.concept(NS.Woman)
    cls_p = reasoner.concept(NS.Person)
    assert reasoner.is_subsumed_by(cls_w, cls_p)

def test_owl_intersection_subclass():
    g, reasoner = graph()

    p = BNode('John')
    g.add((p, RDF.type, NS.Grandfather))

    b0 = BNode()
    b1 = BNode()
    b2 = BNode()

    g.add((b1, RDF.first, NS.Parent))
    g.add((b1, RDF.rest, b2))
    g.add((b2, RDF.first, NS.Man))
    g.add((b2, RDF.rest, RDF.nil))

    g.add((b0, OWL.intersectionOf, b1))
    g.add((NS.Grandfather, RDFS.subClassOf, b0))

    i = reasoner.individual(p)
    cls_p = reasoner.concept(NS.Parent)
    cls_m = reasoner.concept(NS.Man)
    assert reasoner.is_instance(i, cls_p)
    assert reasoner.is_instance(i, cls_m)

def test_owl_intersection_eq_class():
    g, reasoner = graph()

    p = BNode('Alice')
    g.add((p, RDF.type, NS.Parent))
    g.add((p, RDF.type, NS.Woman))

    b0 = BNode()
    b1 = BNode()
    b2 = BNode()

    g.add((b1, RDF.first, NS.Parent))
    g.add((b1, RDF.rest, b2))
    g.add((b2, RDF.first, NS.Woman))
    g.add((b2, RDF.rest, RDF.nil))

    g.add((b0, OWL.intersectionOf, b1))
    g.add((NS.Mother, OWL.equivalentClass, b0))

    i = reasoner.individual(p)
    cls_m = reasoner.concept(NS.Mother)
    assert reasoner.is_instance(i, cls_m)

def test_owl_distinct_members():
    """
    Test OWL distinct members.
    """
    g, reasoner = graph('different_individuals')

    p1 = NS.p1
    p2 = NS.p2
    p3 = NS.p3

    g.add((p1, RDF.type, NS.Man))
    g.add((p2, RDF.type, NS.Man))
    g.add((p3, RDF.type, NS.Man))

    b0 = BNode()
    b1 = BNode()
    b2 = BNode()
    b3 = BNode()
    g.add((b1, RDF.first, p1))
    g.add((b1, RDF.rest, b2))
    g.add((b2, RDF.first, p2))
    g.add((b2, RDF.rest, b3))
    g.add((b3, RDF.first, p3))
    g.add((b3, RDF.rest, RDF.nil))
    g.add((b0, OWL.distinctMembers, b1))

    i1 = reasoner.individual(NS.p1)
    i2 = reasoner.individual(NS.p2)
    i3 = reasoner.individual(NS.p3)
    reasoner.different_individuals.assert_called_once_with([i1, i2, i3])

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

def test_equivalent_classes():
    """
    Test equivalent classes.
    """
    g, reasoner = graph('equal_concepts')

    g.add((NS.P1, OWL.equivalentClass, NS.P2))

    c1 = reasoner.concept(NS.P1)
    c2 = reasoner.concept(NS.P2)
    reasoner.equal_concepts.assert_called_once_with([c1, c2])

def test_disjoin_with():
    """
    Test disjoint classes.
    """
    g, reasoner = graph('disjoint_concepts')

    g.add((NS.P1, OWL.disjointWith, NS.P2))

    c1 = reasoner.concept(NS.P1)
    c2 = reasoner.concept(NS.P2)
    reasoner.disjoint_concepts.assert_called_once_with([c1, c2])

def test_owl_union_of():
    """
    Test OWL union of classes.
    """
    g, reasoner = graph()

    c1 = NS.C1
    c2 = NS.C2
    c3 = NS.C3

    b1 = BNode()
    b2 = BNode()
    g.add((b1, RDF.first, c1))
    g.add((b1, RDF.rest, b2))
    g.add((b2, RDF.first, c2))
    g.add((b2, RDF.rest, RDF.nil))
    g.add((c3, OWL.unionOf, b1))

    g.add((NS.P, RDF.type, c1))

    p = reasoner.individual(NS.P)
    c1 = reasoner.concept(NS.C1)
    c2 = reasoner.concept(NS.C2)
    c3 = reasoner.concept(NS.C3)

    assert not reasoner.is_instance(p, c2)
    assert reasoner.is_instance(p, c3)

def test_rdf_list():
    """
    Test creating RDF list.
    """
    rdf_list = factpp.rdflib.RDFList()
    rdf_list.add('p0', 'p1')     # p0 rdf.rest p1
    rdf_list.add('p1', 'p2')     # p1 rdf.rest p2
    rdf_list.add('p2', 'p3')     # p2 rdf.rest p3
    rdf_list.add('p3', RDF.nil)  # p3 rdf.rest rdf.nil

    rdf_list.set_value('p1', 2)  # p1 rdf.first 2
    rdf_list.set_value('p2', 4)  # p2 rdf.first 4
    rdf_list.set_value('p3', 8)  # p3 rdf.first 8

    result = rdf_list.items(lambda v: v, 'p0')
    assert [2, 4, 8] == list(result)

    g = rdf_list._graph
    assert 'p0' not in g, list(g)
    assert 'p1' not in g, list(g)
    assert 'p2' not in g, list(g)
    assert 'p3' not in g, list(g)

# vim: sw=4:et:ai
