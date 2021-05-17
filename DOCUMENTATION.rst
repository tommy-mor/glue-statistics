
****************************************
Data Viewer Tutorial
****************************************

    :keywords: Tutorial, Documentation

Author: Juna Kim

Introduction
============

This documentation details the funtionality and methods used to create a generic glue viewer. This documentation is also meant to help new Glue developers become aquainted with creating a new viewer and hope to be a resource for kickstarting their own code. Most of the information on this document can be found on the official Glue documentation page, and additional information may be found there. However, this file will be more streamlined to help developers create viewers compared to the original documentation.

Contents
=======================

This section describes the structure of documentation and its files.

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
See link `Toolbar <http://docs.glueviz.org/en/stable/customizing_guide/toolbar.html>`_ for more official documentation

Accessing the Data Collection
=======================
To access the data collection of the current glue session, call the following variable:  

.. code-block:: python

    self.session.data_collection

This will allow you to directly access the data that is in Glue (the top left panel is a visual of what the data collection is).

WARNING: Do not use the variable "dc" in any of your code for the data viewer. The variable "dc" is already being used in the IPython Terminal as a default variable name for the data collection. As a result, it is advised that you use a different variable name to assign the data collection. e.g 
.. code-block:: python

    self.data_c = self.session.data_collection


Listening for Changes with Messages
=======================
A data viewer must be able to be responsive to changes in the glue environment. For example, if a dataset is added/removed from glue, the data viewer may need to update its visual accordingly when it is done so. 

To connect a Message to a method, add the following method into the DataViewer class:

.. code-block:: python

    def register_to_hub(self, hub):
        super(StatsDataViewer, self).register_to_hub(hub)
        
        hub.subscribe(self, "MESSAGE TO LISTEN FOR', handler = 'METHOD TO ACTIVATE WHEN MESSAGE IS RECEIVED')
        #EXAMPLE:
        #hub.subscribe(self, DataCollectionAddMessage, handler = self.newDataAddedMessage)

Replace the 'MESSAGE TO LISTEN FOR' and the 'METHOD TO ACTIVATE WHEN MESSAGE IS RECEIVED' with Messages and methods of your own as done in the example comment below. In the example, the method self.newDataAddedMessage is a method that the user has created, and not a built-in function. This method should update your viewer depending on how the viewer works. 
Plot Layers
=======================
Qt Design
=======================

Pop-up messages
-----------------
Creating the Plugin (and how to update it easily)
=======================
Common bugs and how to fix them
=======================


