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

import rdflib.store

import factpp

class Store(rdflib.store.Store):
    def __init__(self):
        self._reasoner = factpp.Reasoner()

    def add(self, triple, context=None, quoted=False):
        s, p, o = triple

        ref_s = self._reasoner.individual(str(s))
        ref_p = self._reasoner.object_role(str(p))
        value = self._reasoner.individual(str(o))

        self._reasoner.related_to(ref_s, ref_p, value)

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

