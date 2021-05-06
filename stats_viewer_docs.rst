
****************************************
Glue Statistics Viewer Documentation
****************************************

    :keywords: Tutorial, Documentation

Author: Juna Kim

Introduction
============

This documentation details the funtionality and methods used to create Glue's Statistics Viewer. This documentation is also meant to help new Glue developers become aquainted with creating a new viewer and hope to be a resource for kickstarting their own code. Most of the information on this document can be found on the official Glue documentation page, and additional information may be found there. However, this file will be more streamlined to help developers create viewers compared to the original documentation.


Documentation structure
=======================

This section describes the structure of documentation and its files.

Contents
--------

#. How to Use the Statistics Viewer
#. Making the Data Viewer Skeleton
#. Modifying the Toolbar
#. Accessing the Data Collection
#. Listening for Changes with Messages
#. Plot Layers
#. Qt Design
#. Creating the Plugin (and how to update it easily)
#. Common bugs and how to fix them


.. code-block:: rst

    this is a code block
    
``this is highlighted text``

sub section
-----------------

Heading Level 4
^^^^^^^^^^^^^^^

Heading Level 5
"""""""""""""""

links : `TryPyramid <https://trypyramid.com>`_


How to Use the Statistics Viewer
============================


Making the Data Viewer Skeleton
==========================



Modifying the Toolbar
=======================


To create cross-references to a document, arbitrary location, object, or other items, use variations of the following syntax.

*   ``:role:`target``` creates a link to the item named ``target`` of the type indicated by ``role``, with the link's text as the title of the target.
    ``target`` may need to be disambiguated between documentation sets linked through intersphinx, in which case the syntax would be ``deform:overview``.
*   ``:role:`~target``` displays the link as only the last component of the target.
*   ``:role:`title <target>``` creates a custom title, instead of the default title of the target.


.. _dsg-cross-referencing-documents:

Cross-referencing documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To link to pages within this documentation:

.. code-block:: rst

    :doc:`glossary`

The above code renders as follows.

:doc:`glossary`


.. _dsg-cross-referencing-arbitrary-locations:

Cross-referencing arbitrary locations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To support cross-referencing to arbitrary locations in any document and between documentation sets via intersphinx, the standard reST labels are used.
For this to work, label names must be unique throughout the entire documentation including externally linked intersphinx references.
There are two ways in which you can refer to labels, if they are placed directly before a section title, a figure, or table with a caption, or at any other location.
This section has a label with the syntax ``.. _label_name:`` followed by the section title.

.. code-block:: rst

    .. _dsg-cross-referencing-arbitrary-locations:

    Cross-referencing arbitrary locations
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To generate a link to that section with its title, use the following syntax.

.. code-block:: rst

    :ref:`dsg-cross-referencing-arbitrary-locations`

The above code renders as follows.

:ref:`dsg-cross-referencing-arbitrary-locations`

The same syntax works for figures and tables with captions.

For labels that are not placed as mentioned, the link must be given an explicit title, such as ``:ref:`title <label>```.

.. seealso:: See also the Sphinx documentation, :ref:`sphinx:rst-inline-markup`.

