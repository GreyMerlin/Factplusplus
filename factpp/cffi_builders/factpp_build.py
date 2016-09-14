#
# factpp - Python interface to FaCT++ reasoner
#
# Copyright (C) 2016 by Artur Wroblewski <wrobell@riseup.net>
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

import cffi

ffi = cffi.FFI()
ffi.cdef("""
typedef struct fact_reasoning_kernel_st fact_reasoning_kernel;
typedef struct fact_progress_monitor_st fact_progress_monitor;
typedef struct fact_axiom_st fact_axiom;
typedef struct fact_expression_st fact_expression;
typedef struct fact_concept_expression_st fact_concept_expression;
typedef struct fact_role_expression_st fact_role_expression;
typedef struct fact_o_role_expression_st fact_o_role_expression;
typedef struct fact_o_role_complex_expression_st fact_o_role_complex_expression;
typedef struct fact_d_role_expression_st fact_d_role_expression;
typedef struct fact_individual_expression_st fact_individual_expression;
typedef struct fact_data_expression_st fact_data_expression;
typedef struct fact_data_type_expression_st fact_data_type_expression;
typedef struct fact_data_value_expression_st fact_data_value_expression;
typedef struct fact_facet_expression_st fact_facet_expression;
typedef struct fact_actor_st fact_actor;

fact_reasoning_kernel *fact_reasoning_kernel_new(void);
void fact_reasoning_kernel_free(fact_reasoning_kernel *);

fact_concept_expression *fact_concept(fact_reasoning_kernel *k,const char *name);
fact_o_role_expression *fact_object_role (fact_reasoning_kernel *k, const char *name);
fact_concept_expression *fact_o_exists (fact_reasoning_kernel *k, fact_o_role_expression *r, fact_concept_expression *c);
fact_concept_expression *fact_top(fact_reasoning_kernel *k);
fact_axiom *fact_implies_concepts (fact_reasoning_kernel *, fact_concept_expression *c, fact_concept_expression *d);
int fact_is_subsumed_by (fact_reasoning_kernel *, fact_concept_expression *c, fact_concept_expression *d);

fact_actor *fact_concept_actor_new();
fact_actor* fact_individual_actor_new();
fact_actor* fact_o_role_actor_new();
fact_actor* fact_d_role_actor_new();
void fact_actor_free(fact_actor *);

void fact_classify_kb(fact_reasoning_kernel *);

void fact_get_sup_concepts(fact_reasoning_kernel *, fact_concept_expression *c, int direct, fact_actor **actor);
void fact_get_sub_roles (fact_reasoning_kernel *, fact_role_expression *r, int direct, fact_actor **actor);

fact_o_role_expression *fact_object_role_top(fact_reasoning_kernel *k);

const char*** fact_get_elements_2d(fact_actor *);
""")

ffi.set_source('_factpp', """
#include <fact.h>
""", libraries=['fact'], library_dirs=['../FaCT++.C'], include_dirs=['../FaCT++.C'])

# vim: sw=4:et:ai
