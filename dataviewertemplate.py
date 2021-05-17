import os
import numpy as np
import sys
import pandas as pd

@viewer_tool
class ToolbarButton1(Tool):
	"""
    A class used to show the instructions for the Statsviewer in a popup window
    ----------
    Attributes
    ----------
    icon : str
        a formatted string that points to the icon png file location
    tool_id : str
        the id of the refresh tool used to add to toolbar
    action_text : str
        brief description of the tool's function
	tool_tip: str
		detailed tip about the tool's function
	status_tip: str
		message about tool's status
	shortcut: char
		character that can toggle the tool from keyboard
	-------
    Methods
    -------
     __init__(self,viewer):
	 	connects the StatsDataViewerviewer to the tool
	activate(self):
		action performed when tool is activated

    """
	#icon = Logo Here
	tool_id = 'button1'
	action_text = 'button1'
	tool_tip = 'Click for button1'
	status_tip = 'Click'
	shortcut = 'B'

	def __init__(self,viewer):
		self.viewer = viewer

	def activate(self):
		self.viewer.activateToolBarButton1()

	def close(self):
		pass
  
  
  
  
  class MyDataViewer(DataViewer): 
	"""
    A class used to display and make the StatsDataViewer functional
    ----------
    Attributes
    ----------
    LABEL : str
        name of viewer that shows up on the Glue viewer menu
    _state_cls : ViewerState
        ViewerState object of the StatsDataViewer
    _options_cls : ViewerStateWidget
        ViewerStateWidge of the StatsDataViewer
	inherit_tools: boolean
		Sets the inheritance of default tools fromt the BasicToolbar to false
	_toolbar_cls: Toolbar
		The toolbar of the StatsDataViewer
	tools: array
		array of tool ids shown on the StatsDataViewer toolbar
	shortcut: char
		character that can toggle the tool from keyboard
	----------
    """
	LABEL = 'Statistics viewer'
	#_state_cls = StatsViewerState
	#_options_cls = StatsViewerStateWidget
	inherit_tools = False

	_toolbar_cls = BasicToolbar
	tools = ['button1'] #  'expand_tool'

	def __init__(self, *args, **kwargs):
    		'''
		initializes the DataViewer
		'''
		super(MyDataViewer, self).__init__(*args, **kwargs)
    
    
  def register_to_hub(self, hub):
    '''
    connects the StatsDataViewer to Messages that listen for changes to
    the viewer

    @param hub: takes in a HubListener object that can be connected with a Message for listening for changes
    '''
    super(MyDataViewer, self).register_to_hub(hub)
    hub.subscribe(self, DataCollectionAddMessage, handler = self.newDataAddedMessage)
    
  def newDataAddedMessage(self, message):
    print(message)
		index1 = str(message).index("(label: ") + len("(label: ")
		index2 = str(message).index(")")
		newDatasetName = str(message)[index1:index2]
    print("Dataset Added: "+ newDatasetName)
    
qt_client.add(MyDataViewer)
