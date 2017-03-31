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

# distutils: language = c++
# cython: c_string_type=unicode, c_string_encoding=utf8

from libcpp cimport bool
from libcpp.string cimport string
from cython.operator cimport dereference, preincrement

cdef extern from "<vector>" namespace "std":
    cdef cppclass vector[T]:
        T& operator[](int)
        int size()


cdef extern from 'tDLAxiom.h':
    cdef cppclass TDLAxiom:
        TDLAxiom() except +

cdef extern from 'tIndividual.h':
    cdef cppclass TRelatedMap:
        TRelatedMap() except +

    cdef cppclass TIndividual:
        TIndividual(string) except +
        string getName()

cdef extern from 'tRole.h':
    cdef cppclass TRole:
        TRole(string) except +

cdef extern from 'tIndividual.h' namespace 'TRelatedMap':
    ctypedef vector[TIndividual*] CIVec

# cdef extern from 'tNamedEntry.h':
#     cdef cppclass TNamedEntry:
#         TNamedEntry(string) except +
#         string getName()

cdef extern from 'tDLExpression.h':
    cdef cppclass TDLIndividualName:
        TDLIndividualName(string) except +
        string getName()

    cdef cppclass TDLObjectRoleName:
        TDLObjectRoleName(string) except +
        string getName()

    cdef cppclass TDLExpression:
        pass

    cdef cppclass TDLRoleExpression:
        pass

    cdef cppclass TDLObjectRoleComplexExpression(TDLRoleExpression):
        pass

    cdef cppclass TDLObjectRoleExpression(TDLObjectRoleComplexExpression):
        pass

    cdef cppclass TDLDataExpression:
        pass

    cdef cppclass TDLDataValue(TDLDataExpression):
        pass

    cdef cppclass TDLDataTypeExpression(TDLDataExpression):
        pass

    cdef cppclass TDLDataTypeName(TDLDataTypeExpression):
        pass

    cdef cppclass TDLConceptExpression(TDLExpression):
        pass

    cdef cppclass TDLIndividualExpression(TDLExpression):
        pass

    cdef cppclass TDLDataRoleExpression:
        pass

cdef extern from 'tExpressionManager.h':
    cdef cppclass TExpressionManager:
        TDLIndividualExpression* Individual(string)
        TDLObjectRoleExpression* ObjectRole(string)
        TDLDataExpression* DataTop()
        TDLDataTypeName* DataType(string)
        TDLConceptExpression* Concept(string)
        TDLDataRoleExpression* DataRole(string)
        TDLConceptExpression* MaxCardinality(unsigned int, const TDLDataRoleExpression*, const TDLDataExpression*)
        TDLConceptExpression* MaxCardinality(unsigned int, const TDLObjectRoleExpression*, const TDLConceptExpression*)
        const TDLDataValue* DataValue(string, const TDLDataTypeExpression*);

        void newArgList()
        void addArg(const TDLExpression*)


#cdef extern from 'Kernel.h' namespace 'ReasoningKernel':
#    ctypedef vector[TNamedEntry*] IndividualSet

cdef extern from 'Kernel.h':
    cdef cppclass ReasoningKernel:
        ReasoningKernel() except +
        TExpressionManager* getExpressionManager()
        TDLAxiom* setSymmetric(TDLObjectRoleExpression*)
        TDLAxiom* setTransitive(TDLObjectRoleExpression*)
        TDLAxiom* relatedTo(TDLIndividualExpression*, TDLObjectRoleExpression*, TDLIndividualExpression*)
        TDLAxiom* instanceOf(TDLIndividualExpression*, TDLConceptExpression* C)
        TDLAxiom* valueOf(TDLIndividualExpression*, TDLDataRoleExpression*, TDLDataValue*)
        TDLAxiom* setODomain(TDLObjectRoleExpression*, TDLConceptExpression*)
        TDLAxiom* setORange(TDLObjectRoleExpression*, TDLConceptExpression*)
        TDLAxiom* setDDomain(TDLDataRoleExpression*, TDLConceptExpression*)
        TDLAxiom* setDRange(TDLDataRoleExpression*, TDLDataExpression*)

        TDLAxiom* disjointConcepts()
        TDLAxiom* processDifferent()
        TDLAxiom* impliesConcepts(TDLConceptExpression*, TDLConceptExpression*)
        #TIndividual* getIndividual(TDLIndividualExpression*, char*)
        #TRole* getRole(TDLObjectRoleExpression*, char*)
        #CIVec& getRelated(TIndividual*, TRole*)
        #void getRoleFillers(TDLIndividualExpression*, TDLObjectRoleExpression*, IndividualSet&)
        CIVec& getRoleFillers(TDLIndividualExpression*, TDLObjectRoleExpression*)

        void realiseKB()
        bool isKBConsistent()

cdef class Individual:
    cdef const TIndividual *c_obj

    @property
    def name(self):
        return self.c_obj.getName()

cdef class IndividualExpr:
    cdef const TDLIndividualExpression *c_obj

cdef class ConceptExpr:
    cdef const TDLConceptExpression *c_obj

cdef class ObjectRoleExpr:
    cdef const TDLObjectRoleExpression *c_obj

cdef class DataRoleExpr:
    cdef const TDLDataRoleExpression *c_obj

cdef class DataExpr:
    cdef const TDLDataExpression *c_obj

cdef class DataType:
    cdef TDLDataTypeName *c_obj

#cdef class DataValue:
#    cdef TDLDataValue *c_obj

cdef class Reasoner:
    cdef ReasoningKernel *c_kernel

    def __cinit__(self):
        self.c_kernel = new ReasoningKernel()

    def __dealloc__(self):
        del self.c_kernel

    #
    # concepts
    #

    def create_concept(self, name):
        cdef ConceptExpr result = ConceptExpr.__new__(ConceptExpr)
        result.c_obj = self.c_kernel.getExpressionManager().Concept(name)
        return result

    def implies_concepts(self, ConceptExpr c1, ConceptExpr c2):
        self.c_kernel.impliesConcepts(c1.c_obj, c2.c_obj)

    def disjoint_concepts(self, classes):
        self.c_kernel.getExpressionManager().newArgList()
        for c in classes:
            self.c_kernel.getExpressionManager().addArg(
                <TDLConceptExpression*?>(<ConceptExpr>c).c_obj
            )
        self.c_kernel.disjointConcepts()

    #
    # individuals
    #

    def create_individual(self, name):
        cdef IndividualExpr result = IndividualExpr.__new__(IndividualExpr)
        result.c_obj = self.c_kernel.getExpressionManager().Individual(name)
        return result

    def instance_of(self, IndividualExpr i, ConceptExpr c):
        self.c_kernel.instanceOf(i.c_obj, c.c_obj)

    def different_individuals(self, instances):
        self.c_kernel.getExpressionManager().newArgList()
        for i in instances:
            self.c_kernel.getExpressionManager().addArg(
                <TDLIndividualExpression*?>(<IndividualExpr>i).c_obj
            )
        self.c_kernel.processDifferent()

    #
    # object roles
    #

    def create_object_role(self, string name):
        cdef ObjectRoleExpr result = ObjectRoleExpr.__new__(ObjectRoleExpr)
        result.c_obj = self.c_kernel.getExpressionManager().ObjectRole(name)
        return result

    def set_o_domain(self, ObjectRoleExpr r, ConceptExpr c):
        self.c_kernel.setODomain(r.c_obj, c.c_obj)

    def set_o_range(self, ObjectRoleExpr r, ConceptExpr c):
        self.c_kernel.setORange(r.c_obj, c.c_obj)

    def max_o_cardinality(self, unsigned int n, ObjectRoleExpr r, ConceptExpr c):
        cdef ConceptExpr result = ConceptExpr.__new__(ConceptExpr)
        result.c_obj = self.c_kernel.getExpressionManager().MaxCardinality(n, r.c_obj, c.c_obj)
        return result

    def set_symmetric(self, ObjectRoleExpr role):
        self.c_kernel.setSymmetric(role.c_obj)

    def set_transitive(self, ObjectRoleExpr role):
        self.c_kernel.setTransitive(role.c_obj)

    def related_to(self, IndividualExpr i1, ObjectRoleExpr r, IndividualExpr i2):
        self.c_kernel.relatedTo(i1.c_obj, r.c_obj, i2.c_obj)

    def get_role_fillers(self, IndividualExpr i, ObjectRoleExpr r):
        cdef CIVec data = self.c_kernel.getRoleFillers(i.c_obj, r.c_obj)
        cdef Individual result

        for k in range(data.size()):
            result = Individual.__new__(Individual)
            result.c_obj = data[k]
            yield result

    #
    # data roles
    #

    def create_data_role(self, name):
        cdef DataRoleExpr result = DataRoleExpr.__new__(DataRoleExpr)
        result.c_obj = self.c_kernel.getExpressionManager().DataRole(name)
        return result

    def data_top(self):
        cdef DataExpr result = DataExpr.__new__(DataExpr)
        result.c_obj = self.c_kernel.getExpressionManager().DataTop()
        return result

    def data_type(self, name):
        cdef DataType result = DataType.__new__(DataType)
        result.c_obj = self.c_kernel.getExpressionManager().DataType(name)
        return result

    def set_d_domain(self, DataRoleExpr r, ConceptExpr c):
        self.c_kernel.setDDomain(r.c_obj, c.c_obj)

    def set_d_range(self, DataRoleExpr r, DataType t):
        self.c_kernel.setDRange(r.c_obj, t.c_obj)

    def max_d_cardinality(self, unsigned int n, DataRoleExpr r, DataExpr d):
        cdef ConceptExpr result = ConceptExpr.__new__(ConceptExpr)
        result.c_obj = self.c_kernel.getExpressionManager().MaxCardinality(n, r.c_obj, d.c_obj)
        return result

#   def data_value(self, string v, DataType t):
#       cdef DataExpr result = DataExpr.__new__(DataExpr)
#       result.c_obj = self.c_kernel.getExpressionManager().DataValue(v, t.c_obj)
#       return result

    def value_of(self, IndividualExpr i, DataRoleExpr r, int v):
        t = self.c_kernel.getExpressionManager().DataType(b'http://www.w3.org/2001/XMLSchema#integer')
        value = self.c_kernel.getExpressionManager().DataValue(str(v).encode(), t)
        self.c_kernel.valueOf(i.c_obj, r.c_obj, value)

    #
    # general
    #

    def realise(self):
        self.c_kernel.realiseKB()

    def is_consistent(self):
        return self.c_kernel.isKBConsistent()

# vim: sw=4:et:ai
