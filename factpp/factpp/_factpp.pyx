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
from cython.operator cimport dereference, postincrement

cdef extern from "<vector>" namespace "std":
    cdef cppclass vector[T]:
        cppclass iterator:
            T operator*()
            iterator operator++()
            bint operator==(iterator)
            bint operator!=(iterator)

        T& operator[](int)
        int size()
        iterator begin()
        iterator end()


cdef extern from 'taxNamEntry.h':
    cdef cppclass ClassifiableEntry:
        ClassifiableEntry() except +

cdef extern from 'tDLAxiom.h':
    cdef cppclass TDLAxiom:
        TDLAxiom() except +

cdef extern from 'tIndividual.h':
    cdef cppclass TRelatedMap:
        TRelatedMap() except +

    cdef cppclass TIndividual(ClassifiableEntry):
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

    cdef cppclass TDLConceptName(TDLConceptExpression):
        string getName()

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
        TDLConceptName* Concept(string)
        TDLDataRoleExpression* DataRole(string)

        TDLConceptExpression* Top()
        TDLConceptExpression* Bottom()
        TDLConceptExpression* Exists(const TDLObjectRoleExpression*, const TDLConceptExpression*)
        TDLConceptExpression* Exists(const TDLDataRoleExpression*, const TDLDataExpression*)
        TDLObjectRoleExpression* Inverse(const TDLObjectRoleExpression*)


        TDLConceptExpression* Cardinality(unsigned int, const TDLDataRoleExpression*, const TDLDataExpression*)
        TDLConceptExpression* MaxCardinality(unsigned int, const TDLObjectRoleExpression*, const TDLConceptExpression*)
        TDLConceptExpression* MaxCardinality(unsigned int, const TDLDataRoleExpression*, const TDLDataExpression*)

        const TDLDataValue* DataValue(string, const TDLDataTypeExpression*);

        void newArgList()
        void addArg(const TDLExpression*)


#cdef extern from 'Kernel.h' namespace 'ReasoningKernel':
#    ctypedef vector[TNamedEntry*] IndividualSet

cdef extern from 'taxVertex.h':
    cdef cppclass TaxonomyVertex:
        TaxonomyVertex() except +
        const ClassifiableEntry* getPrimer()
        vector[TaxonomyVertex*].iterator begin(bool)
        vector[TaxonomyVertex*].iterator end(bool)

cdef extern from 'Kernel.h':
    cdef cppclass ReasoningKernel:
        ReasoningKernel() except +
        TExpressionManager* getExpressionManager()
        TDLAxiom* setSymmetric(TDLObjectRoleExpression*)
        TDLAxiom* setTransitive(TDLObjectRoleExpression*)
        TDLAxiom* relatedTo(TDLIndividualExpression*, TDLObjectRoleExpression*, TDLIndividualExpression*)
        TDLAxiom* instanceOf(TDLIndividualExpression*, TDLConceptExpression* C)
        bool isInstance(TDLIndividualExpression*, TDLConceptExpression* C)
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
        TaxonomyVertex* setUpCache(TDLConceptExpression*);

        void realiseKB()
        bool isKBConsistent()

cdef class IndividualExpr:
    cdef const TDLIndividualExpression *c_obj

cdef class Individual(IndividualExpr):
    @property
    def name(self):
        return (<TIndividual*>self.c_obj).getName()

cdef class ConceptExpr:
    cdef const TDLConceptExpression *c_obj

cdef class Concept(ConceptExpr):
    @property
    def name(self):
        return (<TDLConceptName*>self.c_obj).getName()

cdef class ObjectRoleExpr:
    cdef const TDLObjectRoleExpression *c_obj

cdef class DataRoleExpr:
    cdef const TDLDataRoleExpression *c_obj

cdef class DataExpr:
    cdef const TDLDataExpression *c_obj

cdef class DataType:
    cdef TDLDataTypeName *c_obj

cdef class Reasoner:
    cdef ReasoningKernel *c_kernel
    cdef TExpressionManager *c_mgr

    cdef readonly DataType type_int
    cdef readonly DataType type_float
    cdef readonly DataType type_str
    cdef readonly DataType type_bool
    cdef readonly DataType type_datetime_long
    cdef readonly dict _cache

    def __cinit__(self):
        self.c_kernel = new ReasoningKernel()
        self.c_mgr = self.c_kernel.getExpressionManager()

    def __init__(self):
        self.type_int = self.data_type('http://www.w3.org/2001/XMLSchema#integer')
        self.type_float = self.data_type('http://www.w3.org/2001/XMLSchema#float')
        self.type_str = self.data_type('http://www.w3.org/2001/XMLSchema#string')
        self.type_bool = self.data_type('http://www.w3.org/2001/XMLSchema#boolean')
        self.type_datetime_long = self.data_type('http://www.w3.org/2001/XMLSchema#dateTimeAsLong')

        self._cache = {}  # it should be weakref dict

    def __dealloc__(self):
        del self.c_kernel

    def _singleton(self, T, key):
        result = self._cache.get(key)
        if result is None:
            result = T.__new__(T)
            self._cache[key] = result
        return result

    #
    # concepts
    #

    def concept(self, str name):
        cdef Concept result = self._singleton(Concept, name)
        result.c_obj = self.c_mgr.Concept(name.encode())
        return result

    def implies_concepts(self, ConceptExpr c1, ConceptExpr c2):
        self.c_kernel.impliesConcepts(c1.c_obj, c2.c_obj)

    def disjoint_concepts(self, classes):
        self.c_mgr.newArgList()
        for c in classes:
            self.c_mgr.addArg((<ConceptExpr>c).c_obj)
        self.c_kernel.disjointConcepts()

    #
    # individuals
    #

    def individual(self, str name):
        cdef Individual result = self._singleton(Individual, name)
        result.c_obj = self.c_mgr.Individual(name.encode())
        return result

    def instance_of(self, IndividualExpr i, ConceptExpr c):
        self.c_kernel.instanceOf(i.c_obj, c.c_obj)

    def different_individuals(self, instances):
        self.c_mgr.newArgList()
        for i in instances:
            self.c_mgr.addArg((<IndividualExpr>i).c_obj)
        self.c_kernel.processDifferent()

    def is_instance(self, IndividualExpr i, ConceptExpr c):
        return self.c_kernel.isInstance(i.c_obj, c.c_obj)

    #
    # object roles
    #
    def _find_role_items(self, ObjectRoleExpr r, bool top):
        cdef Concept result
        cdef const TDLConceptName *obj

        cdef TDLConceptExpression *start = self.c_mgr.Top() if top else self.c_mgr.Bottom()
        cdef TaxonomyVertex *node = self.c_kernel.setUpCache(self.c_mgr.Exists(r.c_obj, start))
        cdef vector[TaxonomyVertex*].iterator it = node.begin(True)

        while it != node.end(True):
            obj = <const TDLConceptName*>dereference(it).getPrimer()
            result = self._cache[obj.getName()]
            yield result
            postincrement(it)

    def object_role(self, str name):
        cdef ObjectRoleExpr result = self._singleton(ObjectRoleExpr, name)
        result.c_obj = self.c_mgr.ObjectRole(name.encode())
        return result

    def set_o_domain(self, ObjectRoleExpr r, ConceptExpr c):
        self.c_kernel.setODomain(r.c_obj, c.c_obj)

    def get_o_domain(self, ObjectRoleExpr r):
        yield from self._find_role_items(r, True)

    def get_o_range(self, ObjectRoleExpr r):
        cdef ObjectRoleExpr rev = ObjectRoleExpr.__new__(ObjectRoleExpr)
        rev.c_obj = r.c_obj
        yield from self._find_role_items(rev, False)

    def set_o_range(self, ObjectRoleExpr r, ConceptExpr c):
        self.c_kernel.setORange(r.c_obj, c.c_obj)

    def max_o_cardinality(self, unsigned int n, ObjectRoleExpr r, ConceptExpr c):
        cdef ConceptExpr result = ConceptExpr.__new__(ConceptExpr)
        result.c_obj = self.c_mgr.MaxCardinality(n, r.c_obj, c.c_obj)
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
            result = self._cache[data[k].getName()]
            yield result

    def get_instances(self, ConceptExpr c, direct=True):
        if not direct:
            raise ValueError('Non-direct instances query not supported yet')

        cdef Individual result
        cdef const TIndividual *obj
        cdef TaxonomyVertex *node = self.c_kernel.setUpCache(c.c_obj)
        cdef vector[TaxonomyVertex*].iterator it = node.begin(False)

        while it != node.end(False):
            obj = <const TIndividual*>dereference(it).getPrimer()
            result = self._cache[obj.getName()]
            yield result
            postincrement(it)

    #
    # data roles
    #

    def data_role(self, str name):
        cdef DataRoleExpr result = self._singleton(DataRoleExpr, name)
        result.c_obj = self.c_mgr.DataRole(name.encode())
        return result

    def data_top(self):
        cdef DataExpr result = DataExpr.__new__(DataExpr)
        result.c_obj = self.c_mgr.DataTop()
        return result

    def data_type(self, str name):
        cdef DataType result = DataType.__new__(DataType)
        result.c_obj = self.c_mgr.DataType(name.encode())
        return result

    def set_d_domain(self, DataRoleExpr r, ConceptExpr c):
        self.c_kernel.setDDomain(r.c_obj, c.c_obj)

    def set_d_range(self, DataRoleExpr r, DataType t):
        self.c_kernel.setDRange(r.c_obj, t.c_obj)

    def d_cardinality(self, unsigned int n, DataRoleExpr r, DataExpr d):
        cdef ConceptExpr result = ConceptExpr.__new__(ConceptExpr)
        result.c_obj = self.c_mgr.Cardinality(n, r.c_obj, d.c_obj)
        return result

    def max_d_cardinality(self, unsigned int n, DataRoleExpr r, DataExpr d):
        cdef ConceptExpr result = ConceptExpr.__new__(ConceptExpr)
        result.c_obj = self.c_mgr.MaxCardinality(n, r.c_obj, d.c_obj)
        return result

#   def data_value(self, string v, DataType t):
#       cdef DataExpr result = DataExpr.__new__(DataExpr)
#       result.c_obj = self.c_mgr.DataValue(v, t.c_obj)
#       return result

    def value_of_int(self, IndividualExpr i, DataRoleExpr r, int v):
        value = self.c_mgr.DataValue(str(v).encode(), self.type_int.c_obj)
        self.c_kernel.valueOf(i.c_obj, r.c_obj, value)

    def value_of_str(self, IndividualExpr i, DataRoleExpr r, str v):
        value = self.c_mgr.DataValue(v.encode(), self.type_str.c_obj)
        self.c_kernel.valueOf(i.c_obj, r.c_obj, value)

    def value_of_float(self, IndividualExpr i, DataRoleExpr r, float v):
        value = self.c_mgr.DataValue(str(v).encode(), self.type_float.c_obj)
        self.c_kernel.valueOf(i.c_obj, r.c_obj, value)

    def value_of_bool(self, IndividualExpr i, DataRoleExpr r, bool v):
        value = self.c_mgr.DataValue(str(v).encode(), self.type_bool.c_obj)
        self.c_kernel.valueOf(i.c_obj, r.c_obj, value)

    #
    # general
    #
    def realise(self):
        self.c_kernel.realiseKB()

    def is_consistent(self):
        return self.c_kernel.isKBConsistent()

# vim: sw=4:et:ai
