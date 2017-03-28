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

from rdflib import Graph, Literal, BNode
from rdflib.namespace import FOAF
from rdflib.store import Store

from _factpp import ffi, lib

class FactStore(Store):
    def __init__(self):
        self._kernel = lib.fact_reasoning_kernel_new()
        self._instances = {}
        self._roles = {}

        self._type_str = lib.fact_data_type(self._kernel, b'http://www.w3.org/2001/XMLSchema#string')

    def add(self, triple, context=None, quoted=False):
        s, p, o = triple

        ref_s = self._instances.get(s)
        if ref_s is None:
            ref_s = lib.fact_individual(self._kernel, s.encode())
            self._instances[str(s)] = ref_s

        ref_p = self._roles.get(p)
        if ref_p is None:
            #ref_p = lib.fact_data_role(self._kernel, p.encode())
            ref_p = lib.fact_object_role(self._kernel, p.encode())
            self._roles[str(p)] = ref_p
            if p == FOAF.knows:
                lib.fact_set_symmetric(self._kernel, ref_p)
                lib.fact_set_transitive(self._kernel, ref_p)

        #value = lib.fact_data_value(self._kernel, o.encode(), self._type_str)
        value = lib.fact_individual(self._kernel, o.encode())
        lib.fact_related_to(self._kernel, ref_s, ref_p, value)

    def triples(self, pattern, context=None):
        s, p, o = pattern
        if s is None:
            for s in self._instances:
                yield from self.role_triples(s, p, context)
        else:
            yield from self.role_triples(s, p, context)

    def role_triples(self, s, p, context):
            ref_s = self._instances[str(s)]
            ref_p = self._roles[str(p)]
            values = lib.fact_get_role_fillers(self._kernel, ref_s, ref_p)
            i = 0
            while values[i] != ffi.NULL:
                yield ((s, p, ffi.string(values[i]).decode()), context)
                i += 1
            
p1 = BNode()
p2 = BNode()
p3 = BNode()

g = Graph(store=FactStore())
g.add((p1, FOAF.name, Literal('P 1')))
g.add((p2, FOAF.name, Literal('P 2')))
g.add((p3, FOAF.name, Literal('P 3')))
g.add((p1, FOAF.knows, p2))
g.add((p2, FOAF.knows, p3))

result = g.query("""
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
SELECT ?n1 ?n2
WHERE {
    ?p1 foaf:knows ?p2.
    ?p1 foaf:name ?n1.
    ?p2 foaf:name ?n2.
}
""")

for r in result:
    print('result', r[0], 'knows', r[1])


# vim: sw=4:et:ai
