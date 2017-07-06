Run an example::

    $ LD_LIBRARY_PATH=../Kernel/obj PYTHONPATH=. python examples/imply-class.py

Try to load FOAF ontology::

    $ LD_LIBRARY_PATH=../Kernel/obj PYTHONPATH=. bin/factpp-load ontologies/foaf.rdf

and print ontology report::

    $ LD_LIBRARY_PATH=../Kernel/obj PYTHONPATH=. bin/factpp-load ontologies/foaf.rdf | ./bin/fact-load-report

      1 metadata: http://purl.org/dc/elements/1.1/description,
      1 metadata: http://purl.org/dc/elements/1.1/title,
      7 metadata: http://www.w3.org/1999/02/22-rdf-syntax-ns#type, http://www.w3.org/2002/07/owl#AnnotationProperty
     75 metadata: http://www.w3.org/2000/01/rdf-schema#comment,
     72 metadata: http://www.w3.org/2000/01/rdf-schema#isDefinedBy,
     78 metadata: http://www.w3.org/2000/01/rdf-schema#label,
     75 metadata: http://www.w3.org/2003/06/sw-vocab-status/ns#term_status,
     62 unsupported: http://www.w3.org/1999/02/22-rdf-syntax-ns#type, http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
      4 unsupported: http://www.w3.org/1999/02/22-rdf-syntax-ns#type, http://www.w3.org/2002/07/owl#FunctionalProperty
     12 unsupported: http://www.w3.org/1999/02/22-rdf-syntax-ns#type, http://www.w3.org/2002/07/owl#InverseFunctionalProperty
      1 unsupported: http://www.w3.org/2000/01/rdf-schema#domain, http://www.w3.org/2002/07/owl#Thing
      1 unsupported: http://www.w3.org/2000/01/rdf-schema#domain, http://xmlns.com/foaf/0.1/Agent
      1 unsupported: http://www.w3.org/2000/01/rdf-schema#range, http://www.w3.org/2000/01/rdf-schema#Literal
      1 unsupported: http://www.w3.org/2000/01/rdf-schema#range, http://xmlns.com/foaf/0.1/Document
     13 unsupported: http://www.w3.org/2000/01/rdf-schema#subPropertyOf,
      8 unsupported: http://www.w3.org/2002/07/owl#disjointWith,
      1 unsupported: http://www.w3.org/2002/07/owl#equivalentProperty,
      8 unsupported: http://www.w3.org/2002/07/owl#inverseOf,

.. vim: sw=4:et:ai
