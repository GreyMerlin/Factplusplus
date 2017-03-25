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
from _factpp import ffi, lib

k = lib.fact_reasoning_kernel_new()
lib.fact_set_verbose_output(k, 1)
lib.fact_kb_set_tracing(k)
lib.fact_kb_set_dump(k)

cls_a = lib.fact_concept(k, b'CLS-A')
cls_b = lib.fact_concept(k, b'CLS-B')

lib.fact_new_arg_list(k)
p_cls_a = ffi.cast('fact_expression*', cls_a)
p_cls_b = ffi.cast('fact_expression*', cls_b)
lib.fact_add_arg(k, p_cls_a)
lib.fact_add_arg(k, p_cls_b)
lib.fact_disjoint_concepts(k)

c = lib.fact_individual(k, b'C')
lib.fact_instance_of(k, c, cls_a)

r = lib.fact_object_role(k, b'R')
lib.fact_set_o_domain(k, r, cls_a)
lib.fact_set_o_range(k, r, cls_b)

restriction_max_one_cls_b = lib.fact_o_max_cardinality(k, 1, r, cls_b)
lib.fact_implies_concepts(k, cls_a, restriction_max_one_cls_b)

d = lib.fact_individual(k, b'D')
lib.fact_instance_of(k, d, cls_b)
lib.fact_related_to(k, c, r, d)

print('consistent', lib.fact_is_kb_consistent(k))
print()

# add another individual to class C, making ontology inconsistent
x = lib.fact_individual(k, b'X')
lib.fact_instance_of(k, x, cls_b)
lib.fact_related_to(k, c, r, x)

lib.fact_new_arg_list(k)
p_d = ffi.cast('fact_expression*', d)
p_x = ffi.cast('fact_expression*', x)
lib.fact_add_arg(k, p_d)
lib.fact_add_arg(k, p_x)
lib.fact_process_different(k)

print('consistent', lib.fact_is_kb_consistent(k))

lib.fact_reasoning_kernel_free(k)

# vim: sw=4:et:ai
