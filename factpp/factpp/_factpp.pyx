# distutils: language = c++
# cython: c_string_type=unicode, c_string_encoding=utf8

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

    cdef cppclass TDLIndividualExpression:
        pass

    cdef cppclass TDLObjectRoleName:
        TDLObjectRoleName(string) except +
        string getName()

#   cdef cppclass TDLRoleExpression:
#       pass
#
#   cdef cppclass TDLObjectRoleComplexExpression(TDLRoleExpression):
#       pass
#
    cdef cppclass TDLObjectRoleExpression: # (TDLObjectRoleComplexExpression):
        pass

cdef extern from 'tExpressionManager.h':
    cdef cppclass TExpressionManager:
        TDLIndividualExpression* Individual(string)
        TDLObjectRoleExpression* ObjectRole(string)

#cdef extern from 'Kernel.h' namespace 'ReasoningKernel':
#    ctypedef vector[TNamedEntry*] IndividualSet

cdef extern from 'Kernel.h':
    cdef cppclass ReasoningKernel:
        ReasoningKernel() except +
        TExpressionManager* getExpressionManager()
        TDLAxiom* setSymmetric(TDLObjectRoleExpression*)
        TDLAxiom* setTransitive(TDLObjectRoleExpression*)
        TDLAxiom* relatedTo(TDLIndividualExpression*, TDLObjectRoleExpression*, TDLIndividualExpression*)
        #TIndividual* getIndividual(TDLIndividualExpression*, char*)
        #TRole* getRole(TDLObjectRoleExpression*, char*)
        #CIVec& getRelated(TIndividual*, TRole*)
        #void realiseKB()
        #void getRoleFillers(TDLIndividualExpression*, TDLObjectRoleExpression*, IndividualSet&)
        CIVec& getRoleFillers(TDLIndividualExpression*, TDLObjectRoleExpression*)

cdef class Individual:
    cdef const TIndividual *c_obj

    @property
    def name(self):
        return self.c_obj.getName()

cdef class IndividualExpr:
    cdef const TDLIndividualExpression *c_obj

cdef class ObjectRoleExpr:
    cdef const TDLObjectRoleExpression *c_obj

cdef class Reasoner:
    cdef ReasoningKernel *c_kernel

    def __cinit__(self):
        self.c_kernel = new ReasoningKernel()

    def __dealloc__(self):
        del self.c_kernel

    def create_individual(self, name):
        cdef IndividualExpr result = IndividualExpr.__new__(IndividualExpr)
        result.c_obj = self.c_kernel.getExpressionManager().Individual(name)
        return result

    def create_object_role(self, string name):
        cdef ObjectRoleExpr result = ObjectRoleExpr.__new__(ObjectRoleExpr)
        result.c_obj = self.c_kernel.getExpressionManager().ObjectRole(name)
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

# vim: sw=4:et:ai
