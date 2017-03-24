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

classes = [
    lib.fact_concept(k, b'A'),
    lib.fact_concept(k, b'B'),
    lib.fact_concept(k, b'C'),
]
p_classes = [ffi.cast('fact_expression*', c) for c in classes]

lib.fact_new_arg_list(k)
for c in p_classes:
    lib.fact_add_arg(k, c)
lib.fact_disjoint_concepts(k)

a = lib.fact_individual(k, b'a')
b = lib.fact_individual(k, b'b')
c = lib.fact_individual(k, b'c')
lib.fact_instance_of(k, a, classes[0])

# inconsistent, b is both instance of class B and C, but B and C are
# disjoint
lib.fact_instance_of(k, b, classes[1])
lib.fact_instance_of(k, b, classes[2])

print('start realise')
lib.fact_realise_kb(k)
print('end realise')

print('consistent', lib.fact_is_kb_consistent(k))

lib.fact_reasoning_kernel_free(k)

# vim: sw=4:et:ai
