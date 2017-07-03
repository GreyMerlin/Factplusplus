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
RDFLib store.
"""

from collections import defaultdict
from functools import partial

import rdflib.store
from rdflib.namespace import RDF, RDFS, OWL

import factpp

class Store(rdflib.store.Store):
    def __init__(self):
        self._reasoner = factpp.Reasoner()
        self._list_cache = ListState.CACHE

    def add(self, triple, context=None, quoted=False):
        s, p, o = triple

        if p is RDF.type:
            ref_s = self._reasoner.individual(str(s))
            ref_o = self._reasoner.concept(str(o))
            self._reasoner.instance_of(ref_s, ref_o)
        elif p is RDFS.subClassOf:
            ref_s = self._reasoner.concept(str(s))
            ref_o = self._reasoner.concept(str(o))
            self._reasoner.implies_concepts(ref_s, ref_o)
        elif p is RDFS.domain:
            ref_s = self._reasoner.object_role(str(s))
            ref_o = self._reasoner.concept(str(o))
            self._reasoner.set_o_domain(ref_s, ref_o)
        elif p is RDFS.range:
            ref_s = self._reasoner.object_role(str(s))
            ref_o = self._reasoner.concept(str(o))
            self._reasoner.set_o_range(ref_s, ref_o)
        elif p is RDF.first:
            self._list_cache[s].first = o
        elif p is RDF.rest:
            self._list_cache[s].rest = o
        elif p == OWL.intersectionOf:
            self._list_cache[o].store = self
            self._list_cache[o].object = o
            self._list_cache[o].subject = s
        else:
            ref_s = self._reasoner.individual(str(s))
            ref_p = self._reasoner.object_role(str(p))
            ref_o = self._reasoner.individual(str(o))

            self._reasoner.related_to(ref_s, ref_p, ref_o)

    def triples(self, pattern, context=None):
        s, p, o = pattern
        if s is None:
            ref_p = self._reasoner.object_role(str(p))
            c = next(self._reasoner.get_o_domain(ref_p))
            for s in self._reasoner.get_instances(c):
                yield from self.role_triples(s.name, p, context)
        else:
            yield from self.role_triples(s, p, context)

    def role_triples(self, s, p, context):
            ref_s = self._reasoner.individual(str(s))
            ref_p = self._reasoner.object_role(str(p))
            objects = self._reasoner.get_role_fillers(ref_s, ref_p)
            for o in objects:
                yield ((s, p, o.name), context)


class ListState:
    """
    RDF list state.

    Used to create subclass of intersection of classes.

    Store subject, first-element and rest-of-list items. Create the
    subclass when all elements are defined.
    """
    def __init__(self):
        self.store = None
        self.object = None

        self._subject = None
        self._first = None
        self._rest = None

    def _set_subject(self, cls):
        self._subject = cls
        self._realise()

    def _set_first(self, cls):
        self._first = cls
        self._realise()

    def _set_rest(self, cls):
        self._rest = cls
        self._realise()

    # a list is realised only when subject, first-element and rest-of-list
    # items are set; caller has to set `store` and `object`
    subject = property(fset=_set_subject)
    first = property(fset=_set_first)
    rest = property(fset=_set_rest)

    def _realise(self):
        if all([self._subject, self._first, self._rest]):
            assert self.object is not None
            assert self.store is not None

            reasoner = self.store._reasoner

            ref_s = reasoner.concept(str(self._subject))
            ref_f = reasoner.concept(str(self._first))
            ref_r = reasoner.concept(str(self._rest))

            cls = reasoner.intersection([ref_f, ref_r])
            reasoner.implies_concepts(cls, ref_s)

            # remove from store
            del ListState.CACHE[self.object]

ListState.CACHE = defaultdict(ListState)

# vim: sw=4:et:ai
