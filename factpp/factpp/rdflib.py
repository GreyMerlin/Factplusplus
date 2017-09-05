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

import logging
from collections import defaultdict
from functools import partial

import rdflib.store
from rdflib.namespace import DC, RDF, RDFS, OWL, Namespace

import factpp

VS = Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')

logger = logging.getLogger(__name__)

class Store(rdflib.store.Store):
    def __init__(self, reasoner=None):
        self._reasoner = reasoner if reasoner else factpp.Reasoner()
        self._list_cache = ListState.CACHE
        self._parsers = {}

        self._create_parsers()

    def _create_parsers(self):
        make_parser = self._make_parser
        as_meta = partial(self._parse_nop, reason='metadata')
        self._parsers = {
            (RDF.type, OWL.Class): self._parse_class,
            (RDF.type, RDFS.Class): self._parse_class,
            (RDF.type, RDF.Property): self._parse_nop,
            (RDF.type, OWL.ObjectProperty): self._parse_o_property,
            (RDF.type, OWL.DatatypeProperty): self._parse_d_property,
            (RDF.type, OWL.FunctionalProperty): self._parse_nop,
            (RDF.type, OWL.InverseFunctionalProperty): self._parse_nop,
            RDF.type: make_parser('instance_of', 'individual', 'concept'),
            RDF.first: self._parse_rdf_first,
            RDF.rest: self._parse_rdf_rest,

            RDFS.subClassOf: make_parser('implies_concepts', 'concept', 'concept'),

            OWL.equivalentClass: make_parser('equal_concepts', 'concept', 'concept', as_list=True),
            OWL.disjointWith: make_parser('disjoint_concepts', 'concept', 'concept', as_list=True),
            OWL.intersectionOf: self._parse_intersection,
            OWL.inverseOf: make_parser('set_inverse_roles', 'object_role', 'object_role'),

            # metadata
            DC.title: as_meta,
            DC.description: as_meta,
            RDFS.comment: as_meta,
            RDFS.label: as_meta,
            RDFS.isDefinedBy: as_meta,
            OWL.versionInfo: as_meta,
            (RDF.type, OWL.AnnotationProperty): as_meta,
            VS.term_status: as_meta,

            None: self._parse_nop,
        }

    def add(self, triple, context=None, quoted=False):
        s, p, o = triple
        if __debug__:
            logger.debug('{}, {}, {}'.format(s, p, o))

        parsers = self._parsers
        keys = ((p, o), (s, p), p, None)

        assert None in parsers
        parse = next(self._parsers.get(k) for k in keys if k in parsers)

        assert parse
        parse(s, o)

    def triples(self, pattern, context=None):
        s, p, o = pattern
        if s is None:
            ref_p = self._reasoner.object_role(p)
            c = next(self._reasoner.get_o_domain(ref_p))
            for s in self._reasoner.get_instances(c):
                yield from self.role_triples(s.name, p, context)
        else:
            yield from self.role_triples(s, p, context)

    def role_triples(self, s, p, context):
        ref_s = self._reasoner.individual(s)
        ref_p = self._reasoner.object_role(p)
        objects = self._reasoner.get_role_fillers(ref_s, ref_p)
        for o in objects:
            yield ((s, p, o.name), context)

    #
    # parsers
    #
    def _make_parser(self, rel, sub, obj, as_list=False):
        f_rel = getattr(self._reasoner, rel)
        f_sub = getattr(self._reasoner, sub)
        f_obj = getattr(self._reasoner, obj)

        if as_list:
            return lambda s, o: f_rel([f_sub(s), f_obj(o)])
        else:
            return lambda s, o: f_rel(f_sub(s), f_obj(o))

    def _parse_intersection(self, s, o):
        self._list_cache[o].store = self
        self._list_cache[o].object = o
        self._list_cache[o].subject = s

    def _parse_rdf_first(self, s, o):
        self._list_cache[s].first = o

    def _parse_rdf_rest(self, s, o):
        self._list_cache[s].rest = o

    def _parse_class(self, s, o):
        self._reasoner.concept(s)
        self._parsers[RDF.type, s] = self._parse_class

    def _parse_o_property(self, s, o):
        r = self._reasoner.object_role(s)
        parsers = self._parsers
        make_parser = self._make_parser
        parsers[s, RDFS.domain] = make_parser('set_o_domain', 'object_role', 'concept')
        parsers[s, RDFS.range] = make_parser('set_o_range', 'object_role', 'concept')
        parsers[RDFS.subPropertyOf, s] = make_parser('implies_o_roles', 'object_role', 'object_role')
        parsers[OWL.equivalentProperty, s] = make_parser('equal_o_roles', 'object_role', 'object_role', as_list=True)
        parsers[s, OWL.equivalentProperty] = make_parser('equal_o_roles', 'object_role', 'object_role', as_list=True)
        parsers[s] = partial(self._parse_related, r)

    def _parse_d_property(self, s, o):
        self._reasoner.data_role(s)

        parsers = self._parsers
        make_parser = self._make_parser
        parsers[s, RDFS.domain] = make_parser('set_d_domain', 'data_role', 'concept')
        parsers[s, RDFS.range] = self._parse_d_range
        parsers[RDFS.subPropertyOf, s] = make_parser('implies_d_roles', 'data_role', 'data_role')
        parsers[OWL.equivalentProperty, s] = make_parser('equal_d_roles', 'data_role', 'data_role', as_list=True)
        parsers[s, OWL.equivalentProperty] = make_parser('equal_d_roles', 'data_role', 'data_role', as_list=True)

    def _parse_d_range(self, s, o):
        r = self._reasoner.data_role(s)
        self._reasoner.set_d_range(r, self._reasoner.type_str)
        self._parsers[s] = partial(self._parse_d_set_str, r)

    def _parse_related(self, role, s, o):
        reasoner = self._reasoner
        ref_s = reasoner.individual(s)
        ref_o = reasoner.individual(o)
        reasoner.related_to(ref_s, role, ref_o)

    def _parse_d_set_str(self, r, s, o):
        i = self._reasoner.individual(s)
        self._reasoner.value_of_str(i, r, str(o))

    def _parse_nop(self, s, o, reason='unsupported'):
        if __debug__:
            logger.debug('skipped: {}'.format(reason))


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

            ref_s = reasoner.concept(self._subject)
            ref_f = reasoner.concept(self._first)
            ref_r = reasoner.concept(self._rest)
            cls = reasoner.intersection([ref_f, ref_r])
            reasoner.equal_concepts([cls, ref_s])

            # remove from store
            del ListState.CACHE[self.object]

ListState.CACHE = defaultdict(ListState)

# vim: sw=4:et:ai
