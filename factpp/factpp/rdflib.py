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
import networkx as nx
from collections import defaultdict
from functools import partial
from networkx.algorithms import shortest_path

import rdflib.store
from rdflib import Literal, URIRef, BNode
from rdflib.namespace import DC, RDF, RDFS, OWL, Namespace

import factpp

logger = logging.getLogger(__name__)


VS = Namespace('http://www.w3.org/2003/06/sw-vocab-status/ns#')

PROPERTY_METHODS = [
    'parse_domain',
    'parse_range',
    'parse_value',
    'parse_sub_property_of',
    'parse_equivalent_property',
    'parse_functional_property',
    'parse_inverse_functional_property',
]


class Store(rdflib.store.Store):
    def __init__(self, reasoner=None):
        self._reasoner = reasoner if reasoner else factpp.Reasoner()
        self._lists = RDFList()
        self._properties = defaultdict(partial(PropertyParser, self))
        self._parsers = {}
        self._anonym = {}  # FIXME: it would be nice to have a solution to
                           # assign an id to a concept in the reasoner
                           # itself

        self._create_parsers()

        # TODO: research the settings below; set all of them to true to
        # allow loading N3 files at the moment
        self.context_aware = True
        self.formula_aware = True

        # keep track of data and object properties, see also
        #
        #   https://bitbucket.org/dtsarkov/factplusplus/issues/76/a-method-to-obtain-existing-object-or-data
        #
        # this is a hack, which would be great to remove
        self._data_properties = set()
        self._object_properties = set()

        # we need to store the values on the side of the store as FaCT++
        # API does not support getting values of a data property, see also
        #
        #     https://bitbucket.org/dtsarkov/factplusplus/issues/55/owl-api-reasoner-interface-lacks
        #
        # this is another hack, which would be great to remove
        self._data_values = {}

    def _create_parsers(self):
        make_parser = self._make_parser
        as_meta = partial(parse_nop, reason='metadata')
        property_parser = lambda f, s, o: getattr(self._properties[s], f)(s, o)
        self._parsers = {
            (RDF.type, OWL.Class): self._parse_class,
            (RDF.type, RDFS.Class): self._parse_class,
            (RDF.type, RDF.Property): self._parse_property,
            (RDF.type, OWL.ObjectProperty): self._parse_o_property,
            (RDF.type, OWL.DatatypeProperty): self._parse_d_property,
            (RDF.type, OWL.FunctionalProperty): partial(property_parser, 'parse_functional_property'),
            (RDF.type, OWL.InverseFunctionalProperty): partial(property_parser, 'parse_inverse_functional_property'),

            RDFS.domain: partial(property_parser, 'parse_domain'),
            RDFS.range: partial(property_parser, 'parse_range'),
            RDFS.subPropertyOf: partial(property_parser, 'parse_sub_property_of'),
            OWL.equivalentProperty: partial(property_parser, 'parse_equivalent_property'),
            OWL.inverseOf: make_parser('set_inverse_roles', 'object_role', 'object_role'),
            OWL.propertyChainAxiom: self._parse_property_chain,

            RDF.type: make_parser('instance_of', 'individual', 'concept'),
            RDF.first: self._parse_rdf_first,
            RDF.rest: self._parse_rdf_rest,

            RDFS.subClassOf: make_parser('implies_concepts', 'concept', 'concept'),

            OWL.equivalentClass: make_parser('equal_concepts', 'concept', 'concept', as_list=True),
            OWL.disjointWith: make_parser('disjoint_concepts', 'concept', 'concept', as_list=True),
            OWL.intersectionOf: self._parse_intersection,
            OWL.distinctMembers: self._parse_distinct_members,

            # metadata
            DC.title: as_meta,
            DC.description: as_meta,
            RDFS.comment: as_meta,
            RDFS.label: as_meta,
            RDFS.isDefinedBy: as_meta,
            OWL.versionInfo: as_meta,
            (RDF.type, OWL.AnnotationProperty): as_meta,
            VS.term_status: as_meta,

            None: parse_nop,
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
            ref_p, get_domain, _ = self._property_type(p)
            c = next(get_domain(ref_p))
            for s in self._reasoner.get_instances(c):
                yield from self.role_triples(s.name, p, context)
        else:
            yield from self.role_triples(s, p, context)

    def role_triples(self, s, p, context):
        ref_s = self._reasoner.individual(s)
        ref_p, _, fetch_values = self._property_type(p)
        values = fetch_values(ref_s, ref_p)
        return (((s, p, v), context) for v in values)

    def remove(self, triple, context=None):
        logger.warning('removal of triples not supported yet')

    def _fetch_data_values(self, ref_s, ref_p):
        v = self._data_values.get((ref_s, ref_p))
        if v:
            yield v

    def _fetch_object_values(self, ref_s, ref_p):
        objects = self._reasoner.get_role_fillers(ref_s, ref_p)
        return (o.name for o in objects)

    def _property_type(self, p):
        reasoner = self._reasoner
        if p in self._data_properties:
            return reasoner.data_role(p), reasoner.get_d_domain, self._fetch_data_values
        elif p in self._object_properties:
            return reasoner.object_role(p), reasoner.get_o_domain, self._fetch_object_values
        else:
            return None, None, None

    #
    # parsers
    #
    def _make_parser(self, rel, sub, obj, as_list=False):
        def fetcher(f):
            return lambda s: self._anonym[s] if s in self._anonym else f(s)

        f_rel = getattr(self._reasoner, rel)
        f_sub = fetcher(getattr(self._reasoner, sub))
        f_obj = fetcher(getattr(self._reasoner, obj))

        if as_list:
            return lambda s, o: f_rel([f_sub(s), f_obj(o)])
        else:
            return lambda s, o: f_rel(f_sub(s), f_obj(o))

    def _parse_intersection(self, s, o):
        # FIXME: this works assuming OWL.intersectionOf is executed once
        # the list is constructed
        self._lists.add(s, o)
        items = self._lists.items(self._reasoner.concept, s)
        c = self._reasoner.intersection(list(items))
        self._anonym[s] = c

    def _parse_distinct_members(self, s, o):
        # FIXME: this works assuming OWL.distinctMembers is executed once
        # the list is constructed
        self._lists.add(s, o)
        items = self._lists.items(self._reasoner.individual, s)
        c = self._reasoner.different_individuals(list(items))
        self._anonym[s] = c

    def _parse_property_chain(self, s, o):
        self._lists.add(s, o)
        items = self._lists.items(self._reasoner.object_role, s)
        ref_s = self._reasoner.object_role(s)
        c = self._reasoner.compose(*items)
        self._reasoner.implies_o_roles(c, ref_s)

    def _parse_rdf_first(self, s, o):
        self._lists.set_value(s, o)

    def _parse_rdf_rest(self, s, o):
        self._lists.add(s, o)

    def _parse_class(self, s, o):
        self._parsers[RDF.type, s] = self._make_parser(
            'instance_of', 'individual', 'concept'
        )

    def _parse_property(self, s, o):
        p = self._properties[s]  # defaultdict used to store, so property
                                 # is auto created
        assert isinstance(p, PropertyParser)

        # unknown property type (object or data property) at this stage
        p._name = s
        self._parsers[s] = p._parse_value_unknown

    def _parse_o_property(self, s, o):
        p = self._properties[s]
        assert p._type != 'data'

        role = self._reasoner.object_role(s)
        p.set_role('object', s, role)
        self._parsers[s] = p.parse_value

        self._object_properties.add(s)

    def _parse_d_property(self, s, o):
        p = self._properties[s]
        assert p._type != 'object'

        role = self._reasoner.data_role(s)
        p.set_role('data', s, role)
        self._parsers[s] = p.parse_value

        self._data_properties.add(s)


class PropertyParser:
    """
    Property parser.

    If property has unknown type, then statements to be parsed are stored
    in parser cache.

    :var _cache: Parser cache.
    """
    def __init__(self, store):
        self._name = None
        self._role = None
        self._type = None
        self._cache = set()

        self._store = store

        # create methods to cache property parsing calls while a property
        # type is unknown
        for dest in PROPERTY_METHODS:
            setattr(self, dest, partial(self._cache_call, dest))

    @property
    def _reasoner(self):
        return self._store._reasoner

    def set_role(self, type, name, role):
        self._name = name
        self._role = role
        self._type = type

        for dest in PROPERTY_METHODS:
            source = '_{}_{}'.format(type, dest)
            method = getattr(self, source)
            setattr(self, dest, method)

        for dest, s, o in self._cache:
            method = getattr(self, dest)
            method(s, o)

    def _cache_call(self, dest, s, o):
        self._cache.add((dest, s, o))

    def _parse_value_unknown(self, s, o):
        """
        Parse value for a property of an unknown type.

        Determine value of the property and set its type, this is data or
        object property, depending on the type.

        data property
            `Literal`
        object property
            `BNode`, `URIRef`
        """
        if isinstance(o, Literal):
            ref_p = self._reasoner.data_role(self._name)
            type = 'data'
        elif isinstance(o, (URIRef, BNode)):
            ref_p = self._reasoner.object_role(self._name)
            type = 'object'
        else:
            assert False, 'Unknown property value type: {}'.format(type(o))

        self.set_role(type, self._name, ref_p)
        self.parse_value(s, o)

    #
    # Methods, which names follow the pattern:
    #
    #   _{type}_{dest}
    #
    # Type is `data` or `object` for data and object properties. The `dest`
    # is one property operations listed in `PROPERTY_METHODS`.
    #

    def _object_parse_domain(self, s, o):
        ref_o = self._reasoner.concept(o)
        self._reasoner.set_o_domain(self._role, ref_o)

    def _data_parse_domain(self, s, o):
        ref_o = self._reasoner.concept(o)
        self._reasoner.set_d_domain(self._role, ref_o)

    def _object_parse_range(self, s, o):
        ref_o = self._reasoner.concept(o)
        self._reasoner.set_o_range(self._role, ref_o)

    def _data_parse_range(self, s, o):
        # FIXME: allow different types
        self._reasoner.set_d_range(self._role, self._reasoner.type_str)

    def _object_parse_value(self, s, o):
        reasoner = self._reasoner
        ref_s = reasoner.individual(s)
        ref_o = reasoner.individual(o)
        reasoner.related_to(ref_s, self._role, ref_o)

    def _data_parse_value(self, s, o):  # strings supported at the moment only
        i = self._reasoner.individual(s)
        self._reasoner.value_of_str(i, self._role, str(o))
        self._store._data_values[(i, self._role)] = o

    def _object_parse_equivalent_property(self, s, o):
        ref_o = self._reasoner.object_role(o)
        self._reasoner.equal_o_roles([self._role, ref_o])

    def _data_parse_equivalent_property(self, s, o):
        ref_o = self._reasoner.data_role(o)
        self._reasoner.equal_d_roles([self._role, ref_o])

    def _object_parse_sub_property_of(self, s, o):
        ref_o = self._reasoner.object_role(o)
        self._reasoner.implies_o_roles(self._role, ref_o)

    def _data_parse_sub_property_of(self, s, o):
        ref_o = self._reasoner.data_role(o)
        self._reasoner.implies_d_roles(self._role, ref_o)

    def _object_parse_functional_property(self, s, o):
        self._reasoner.set_o_functional(self._role)

    def _data_parse_functional_property(self, s, o):
        self._reasoner.set_d_functional(self._role)

    def _object_parse_inverse_functional_property(self, s, o):
        self._reasoner.set_inverse_functional(self._role)

    def _data_parse_inverse_functional_property(self, s, o):
        parse_nop()


class RDFList:
    """
    Graph of RDF lists.

    All RDF lists are stored as graph.

    Once a RDF list is complete, then shortest path between head of the
    list and `RDF.nil` contains the list elements.
    """
    def __init__(self):
        self._graph = nx.DiGraph()

    def add(self, n1, n2):
        self._graph.add_edge(n1, n2)

    def set_value(self, node, value):
        self._graph.add_node(node, value=value)

    def items(self, f, start):
        path = shortest_path(self._graph, start, RDF.nil)
        path = path[:-1]
        nodes = self._graph.nodes()
        items = (nodes[p] for p in path)
        items = (p for p in items if p)
        yield from (f(p['value']) for p in items)
        self._graph.remove_node(start)
        self._graph.remove_nodes_from(path)


def parse_nop(*args, reason='unsupported'):
    if __debug__:
        logger.debug('skipped: {}'.format(reason))


# vim: sw=4:et:ai
