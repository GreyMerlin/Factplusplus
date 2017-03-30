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

kernel = factpp.Reasoner()

c = kernel.create_individual(b'C')
d = kernel.create_individual(b'D')
e = kernel.create_individual(b'E')
r = kernel.create_object_role(b'R')

kernel.set_symmetric(r)
kernel.set_transitive(r)
kernel.related_to(c, r, d)
kernel.related_to(d, r, e)

values = kernel.get_role_fillers(d, r)
for v in values:
    print(v.name)

# vim: sw=4:et:ai
