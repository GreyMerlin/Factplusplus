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

def test_intersection():
    """
    Test intersection of classes.

    From OWL 2 primer::

        SubClassOf(
          :Father 
          ObjectIntersectionOf(:Man :Parent)
        )
    """
    reasoner = Reasoner()

    cls_p = reasoner.concept('Parent')
    cls_m = reasoner.concept('Man')
    cls_f = reasoner.concept('Father')

    cls_uf = reasoner.intersection([cls_p, cls_m])
    reasoner.implies_concepts(cls_uf, cls_f)

    i = reasoner.individual('John')
    reasoner.instance_of(i, cls_m)
    reasoner.realise()

    # is a man, but not a parent yet
    assert not reasoner.is_instance(i, cls_f)

    # is a parent, so father as well
    reasoner.instance_of(i, cls_p)
    reasoner.realise()
    assert reasoner.is_instance(i, cls_f)

# vim: sw=4:et:ai
