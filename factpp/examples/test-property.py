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

c = reasoner.create_individual('C')
d = reasoner.create_individual('D')
e = reasoner.create_individual('E')
r = reasoner.create_object_role('R')

reasoner.set_symmetric(r)
reasoner.set_transitive(r)
reasoner.related_to(c, r, d)
reasoner.related_to(d, r, e)

values = reasoner.get_role_fillers(d, r)
for v in values:
    print(v.name)

# vim: sw=4:et:ai
