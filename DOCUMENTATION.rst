
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



Making the Data Viewer Skeleton
==========================

In order to create a viewer, you will need to override the DataViewer class

Modifying the Toolbar
=======================
See link `Toolbar <http://docs.glueviz.org/en/stable/customizing_guide/toolbar.html>`_ for more official documentation

Accessing the Data Collection
=======================
To access the data collection of the current glue session, call the following variable:  

.. code-block:: python

    self.session.data_collection

This will allow you to directly access the data that is in Glue (the top left panel is a visual of what the data collection is).

**WARNING**: Do not use the variable "dc" in any of your code for the data viewer. The variable "dc" is already being used in the IPython Terminal as a default variable name for the data collection. If you use the variable "dc", then the IPython Terminal will break and not be able to call "dc". As a result, use a different variable name to assign the data collection. e.g

.. code-block:: python
    
    self.data_c = self.session.data_collection


Listening for Changes with Messages
=======================
A data viewer must be able to be responsive to changes in the glue environment. For example, if a dataset is added to glue, the data viewer may need to update its visual accordingly to add the newly added dataset. A viewer may also need to be updated if a dataset is delted, modified, etc. The action (dataset added, removed, modified, etc) that Glue listens for is called a ``Message``. If the a particulat action is performed, the corresponding Message is activated. With this activation, you can add more functionality to your viewer so it can update accordingly. 

link: `Full List of Messages <http://docs.glueviz.org/en/stable/_modules/glue/core/message.html#Message>`_

Messages:
-----------------

Most common:

* **DataCollectionAddMessage**: Activates when a new dataset is added
* **DataCollectionDeleteMessage**: Activates when a dataset is deleted
* **DataUpdateMessage**: Activates when a dataset is finished updating
* **SubsetCreateMessage**: Activates when a new subset is created
* **SubsetDeleteMessage**: Activates when a new subset is deleted
* **EditSubsetMessage**: Activates when a new subset is being edited 
* **SubsetUpdateMessage**: Activates when a subset is finished updating
* **ExternallyDerivableComponentsChangedMessage**: Activates when any datasets are linked

Updates/Edits to a Dataset/Subset include the name, color, and size as well!

Other Messages:

* **DataCollectionMessage**: Activates when any change to DataCollection made(add/delete/modified)
* **DataAddComponentMessage**: Activates when a component is added to the data
* **DataRemoveComponentMessage**: Activates when a component is deleted from the data
* **LayerArtistVisibilityMessage**: Activates when a plot layer check is turned on/off (see middle left panel) 
* **LayerArtistUpdatedMessage**: Activates when any part of the LayerArtist changes (creating a new viewer, new subset, new data)
* **ExternallyDerivableComponentsChangedMessage**: Activates when any datasets are linked 

See the full list of `Messages <http://docs.glueviz.org/en/stable/_modules/glue/core/message.html#Message>`_

To connect a Message to a method, add the following method into the DataViewer class:

.. code-block:: python

    def register_to_hub(self, hub):
        super(StatsDataViewer, self).register_to_hub(hub)
        
        #hub.subscribe(self, "MESSAGE TO LISTEN FOR', handler = 'METHOD TO ACTIVATE WHEN MESSAGE IS ACTIVATED')
        #EXAMPLE:
        hub.subscribe(self, DataCollectionAddMessage, handler = self.newDataAddedMessage)

Replace the 'MESSAGE TO LISTEN FOR' and the 'METHOD TO ACTIVATE WHEN MESSAGE IS RECEIVED' with Messages and methods of your own as done in the example comment below. In the example, the method self.newDataAddedMessage is a method that the user has created, and not a built-in function. This method should update your viewer depending on how the viewer works. In the above example, the method newDataAddedMessage() will be activated when a new dataset is imported into Glue.

When a Message is sent to the method you "subscribed"/connected it to, the function intakes a String Message as a parameter. It is with this String Message you can determine which data/subset sent the message as well as its new values. A good starting point to gather more information about the Message is to take apart or print the String Message as done in the example:

.. code-block:: python
    
    def newDataAddedMessage(self, message):
		print(message)
		index1 = str(message).index("(label: ") + len("(label: ")
		index2 = str(message).index(")")
		newDataSetName = str(message)[index1:index2]
        
        #Now you know the new dataset name, add more code as necessary to update your viewer or get more info out of the message string
                 
It is important to note that each Messages can send unique Message String formats, so make sure that when you splice the string you are doing it properly for each message.

Plot Layers
=======================
The plot layer is the left middle panel on Glue. Here, the user can toggle which data or subsets are visible, drag them around for reordering, as well as change other attributes of the particular data. In order to make the plot layer interactive with your viewer, you must connect a method (adding a callback) that activates everytime the plot layer changes. This can be done in the following line of code that goes in the __init__ method of the DataViewer.

.. code-block:: python

    self.state.add_callback('layers', self.exampleCallbackMethod)
    
    
The method that is connected to the plot layers will need to intake a callback list. A call back list is simply a list that has a method connected to it. **what is that method**




Qt Design
=======================

Pop-up messages
-----------------

Creating the Plugin (and how to update it easily)
=======================

`See info in official documentation <http://docs.glueviz.org/en/stable/customizing_guide/writing_plugin.html>`_

Up until now, the code was written in a file named config.py, which could simply be placed in the working directory. In order to transform your config.py file into a Glue plugin, follow the instructions from the official `documentation <http://docs.glueviz.org/en/stable/customizing_guide/writing_plugin.html>`_ and template on the https://github.com/glue-viz/glue-plugin-template to create a new github repository for your viewer. 

Your repository should have:

* A folder name YOURDATAVIEWER
	* The config.py file renamed as YOURDATAVIEWER.py
	* __init__.py
	* version.py
	* Any additional files you might need(.pngs, .ui , etc)
	
* setup.py
* setup.cfg

If you are confused on what your repository should look like, see the `Glue Statistics Viewer Repository <https://github.com/jk31768/glue-statistics>`_ for inspiration




Common bugs and how to fix them
=======================


