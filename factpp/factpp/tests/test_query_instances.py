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

from .._factpp import Reasoner

def test_instances_query():
    reasoner = Reasoner()

    cls = reasoner.concept('CLS')
    for v in 'abc':
        i = reasoner.individual(v)
        reasoner.instance_of(i, cls)

    reasoner.realise()

    names = [i.name for i in reasoner.get_instances(cls)]
    assert ['a', 'b', 'c'] == names


# vim: sw=4:et:ai
