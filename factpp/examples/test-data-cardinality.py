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

import factpp

reasoner = factpp.Reasoner()
#lib.fact_set_verbose_output(k, 1)
#lib.fact_kb_set_tracing(k)
#lib.fact_kb_set_dump(k)

top_data = reasoner.data_top()
type_integer = reasoner.data_type(b'http://www.w3.org/2001/XMLSchema#integer')

cls_a = reasoner.create_concept(b'CLS-A')
c = reasoner.create_individual(b'C')
reasoner.instance_of(c, cls_a)

r = reasoner.create_data_role(b'R')
lib.fact_set_d_domain(k, r, cls_a)
lib.fact_set_d_range(k, r, p_type_integer)

restriction_max_one = lib.fact_d_max_cardinality(k, 1, r, top_data)
lib.fact_implies_concepts(k, cls_a, restriction_max_one)

value = lib.fact_data_value(k, b'1', type_integer)
lib.fact_value_of(k, c, r, value)
print('consistent', lib.fact_is_kb_consistent(k))

print()
value = lib.fact_data_value(k, b'2', type_integer)
lib.fact_value_of(k, c, r, value)
print('consistent', lib.fact_is_kb_consistent(k))

# vim: sw=4:et:ai
