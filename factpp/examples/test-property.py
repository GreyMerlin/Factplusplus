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

c = lib.fact_individual(k, b'C')
d = lib.fact_individual(k, b'D')
e = lib.fact_individual(k, b'E')
r = lib.fact_object_role(k, b'R')

lib.fact_set_symmetric(k, r)
lib.fact_set_transitive(k, r)
lib.fact_related_to(k, c, r, d)
lib.fact_related_to(k, d, r, e)

values = lib.fact_get_role_fillers(k, d, r)
i = 0
while values[i] != ffi.NULL:
    s = ffi.string(values[i]).decode()
    print(s)
    i += 1

lib.fact_reasoning_kernel_free(k)

# vim: sw=4:et:ai
