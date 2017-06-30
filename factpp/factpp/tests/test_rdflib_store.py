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
from rdflib.namespace import FOAF, RDF, RDFS

import factpp.rdflib
from .._factpp import Reasoner

def graph():
    g = Graph(store=factpp.rdflib.Store())
    return g, g.store._reasoner

def test_property_domain():
    g, reasoner = graph()
    g.add((FOAF.knows, RDFS.domain, FOAF.Person))

    r = reasoner.object_role(str(FOAF.knows))
    value = next(reasoner.get_o_domain(r))
    assert value.name == str(FOAF.Person)

def test_property_range():
    g, reasoner = graph()
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

# vim: sw=4:et:ai
