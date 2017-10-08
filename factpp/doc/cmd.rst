Run an example::

    $ LD_LIBRARY_PATH=../Kernel PYTHONPATH=. python examples/imply-class.py

Try to load FOAF ontology::

    $ LD_LIBRARY_PATH=../Kernel PYTHONPATH=. bin/factpp-load ontologies/foaf.rdf

and print ontology report::

    $ LD_LIBRARY_PATH=../Kernel PYTHONPATH=. bin/factpp-load ontologies/foaf.rdf 2>&1 | bin/factpp-load-report

      1 metadata: http://purl.org/dc/elements/1.1/description,
      1 metadata: http://purl.org/dc/elements/1.1/title,
      6 metadata: http://www.w3.org/1999/02/22-rdf-syntax-ns#type, http://www.w3.org/2002/07/owl#AnnotationProperty
     23 metadata: http://www.w3.org/2000/01/rdf-schema#comment,
     20 metadata: http://www.w3.org/2000/01/rdf-schema#isDefinedBy,
     25 metadata: http://www.w3.org/2000/01/rdf-schema#label,
     23 metadata: http://www.w3.org/2003/06/sw-vocab-status/ns#term_status,


.. vim: sw=4:et:ai
