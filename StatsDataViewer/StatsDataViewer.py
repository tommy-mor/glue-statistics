import os
import numpy as np
import sys
import pandas as pd
from qtpy.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QTreeWidget, QTreeWidgetItem, QAbstractItemView, QPushButton
from glue.config import qt_client
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.core.data_factories import load_data
from glue.external.echo import CallbackProperty, SelectionCallbackProperty
from glue.external.echo.qt import (connect_checkable_button,
								   autoconnect_callbacks_to_qt,
								   connect)
from PyQt5.QtCore import QVariant, QItemSelectionModel, QAbstractItemModel, Qt
from glue.config import viewer_tool
from glue.viewers.common.qt.tool import CheckableTool, Tool
from glue.viewers.common.layer_artist import LayerArtist
from glue.viewers.common.state import ViewerState, LayerState
from glue.viewers.common.qt.data_viewer import DataViewer
from glue.viewers.common.qt.toolbar import BasicToolbar
from glue.utils.qt import load_ui
from decimal import getcontext, Decimal
from glue.core import DataCollection, Hub, HubListener, Data, coordinates
from glue.core.message import  DataMessage, DataCollectionMessage, SubsetMessage, SubsetCreateMessage, SubsetUpdateMessage, \
	LayerArtistUpdatedMessage, NumericalDataChangedMessage, DataUpdateMessage, DataAddComponentMessage, DataRemoveComponentMessage, DataCollectionDeleteMessage,\
	SubsetDeleteMessage, EditSubsetMessage, DataCollectionActiveChange
from PyQt5.QtGui import QStandardItemModel
from PyQt5 import QtGui
from PyQt5.QtWidgets import QAction, QTabWidget
from glue.icons.qt import helpers
from qtpy import compat, QtWidgets
from glue.config import auto_refresh
auto_refresh(True)

from StatsDataViewer import REFRESH_LOGO, NOTATION_LOGO, EXPORT_LOGO, CALCULATE_LOGO, SORT_LOGO

@viewer_tool
class Refresh(Tool):
	"""
	A class used to represent the refresh button on the toolbar
	----------
	Attributes
	----------
	icon : str
	a formatted string that points to the icon png file location
	tool_id : str
	the id of the refresh tool used to add to toolbar
	action_text : str
	brief description of the tool's function
	-------
	Methods
	-------
	__init__(self,viewer):
		connects the StatsDataViewerviewer to the tool
	activate(self):
		action performed when tool is activated
   	"""
	icon = REFRESH_LOGO
	tool_id = 'refresh'
	action_text = 'Refresh'

	def __init__(self,viewer):
		self.viewer = viewer
	def activate(self):
		self.viewer.refresh()

@viewer_tool
class SelectDecimalPoints(Tool):
	#icon = '/Users/jk317/Glue/icons/glue_scientific_notation.png'
	tool_id = 'decimal_place'
	action_text = 'Convert'

	def __init__(self,viewer):
		self.viewer = viewer

	def menu_actions(self):
		result = []
		a = QtWidgets.QAction("Decimal Points", None)
		a.triggered.connect(self.test)
		result.append(a)
		a = QtWidgets.QAction("Points", None)
		a.triggered.connect(self.test)
		result.append(a)
		return result
	def test(self):
		print("test")
#	def activate(self):
	#	self.viewer.test2()

@viewer_tool
class ConvertNotation(Tool):
	"""
	A class used to convert calculated values on the viewer to decimal or
	scientific notation
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
	icon = NOTATION_LOGO
	tool_id = 'notation_tool'
	action_text = 'Convert'
	tool_tip = 'Click icon to toggle Scientific noation or decimal'
	status_tip = 'Click to toggle notation'
	shortcut = 'N'

	def __init__(self,viewer):
		self.viewer = viewer

	def activate(self):
		#self.icon = '/Users/jk317/Glue/icons/glue_scientific_notation.png'
		#print("Convert button activate")
		self.viewer.pressedEventConvertNotation(not self.viewer.isSci)

	def close(self):
		pass

@viewer_tool
class ExportButton(Tool):
	"""
	A class used to export calculated values of the active viewer
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
	icon = EXPORT_LOGO
	tool_id = 'export_tool'
	action_text = 'Export'
	tool_tip = 'Click icon to export'
	status_tip = 'Click to export'
	shortcut = 'F'

	def __init__(self,viewer):
		self.viewer = viewer

	def activate(self):
		#print("Export button activate")
		self.viewer.pressedEventExport()
		#print(self.viewer.layers[0].layer)

	def close(self):
		pass

@viewer_tool
class HomeButton(Tool):
	"""
	A class used to shrink every tree item of the active viewer
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
	icon = 'glue_home'
	tool_id = 'home_tool'
	action_text = 'Home'
	tool_tip = 'Click to return to home'
	status_tip = 'Click to return to home'
	shortcut = 'H'

	def __init__(self, viewer):
		self.viewer = viewer

	def activate(self):
		if self.viewer.tabs.currentIndex() == 0:
			self.viewer.subsetTree.collapseAll()
		elif self.viewer.tabs.currentIndex() == 1:
			self.viewer.componentTree.collapseAll()

	def close(self):
		pass

@viewer_tool
class TreeButton(Tool):

	#icon = '/Users/jk317/Glue/icons/glue_hierarchy.png'
	tool_id = 'move_tool'
	action_text = 'switch view'
	tool_tip = 'toggle view'
	status_tip = 'toggle view'
	shortcut = 'M'

	def __init__(self, viewer):
		self.viewer = viewer

	def activate(self):
		self.viewer.sortByComponents()
		self.viewer.component_mode = True

	def close(self):
		pass

@viewer_tool
class ExpandButton(Tool):

	#icon = '/Users/jk317/Glue/icons/glue_expand.png'
	tool_id = 'expand_tool'
	action_text = 'expand'
	tool_tip = 'Click to expand all data and subsets'
	status_tip = 'Click to expand'
	shortcut = 'E'

	def __init__(self, viewer):
		self.viewer = viewer
		self.toExpand = True

	def activate(self):
		self.viewer.expandAll(self.toExpand)
		self.toExpand = not self.toExpand

	def close(self):
		pass

@viewer_tool
class CalculateButton(Tool):
	"""
	A class used to calculate values that are checked on the viewer
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
	icon = CALCULATE_LOGO
	tool_id = 'calc_tool'
	action_text = 'Calculate'
	tool_tip = 'Click side icons to calculate'
	status_tip = 'Click to calculate'
	shortcut = 'C'

	def __init__(self, viewer):
		self.viewer = viewer

	def activate(self):
		#print("Calculate button activate")
		self.viewer.pressedEventCalculate(False)
		#print(self.viewer.layers[0].layer)

	def close(self):
		pass

@viewer_tool
class SortButton(Tool):
	"""
	A class used to sort calculated values 
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
	icon = SORT_LOGO
	tool_id = 'sort_tool'
	action_text = 'Sort'
	tool_tip = 'Click side icons to sort'
	status_tip = 'Choose a column to sort by. When you are done, deactivate sort mode.'
	shortcut = 'S'

	def __init__(self, viewer):
		#super(Tool, self).__init__(viewer)
		 self.viewer = viewer

	def activate(self):
		if self.viewer.tabs.currentIndex() == 0:
			if self.viewer.subsetTree.isSortingEnabled():
				self.viewer.subsetTree.setSortingEnabled(False)
			else:
				self.viewer.subsetTree.setSortingEnabled(True)
		elif self.viewer.tabs.currentIndex() == 1:
			if self.viewer.componentTree.isSortingEnabled():
				self.viewer.componentTree.setSortingEnabled(False)
			else:
				self.viewer.componentTree.setSortingEnabled(True)

	def close(self):
		pass


class StatsViewerState(ViewerState):

	def __init__(self, *args, **kwargs):
		super(StatsViewerState, self).__init__(*args, **kwargs)
		self.expandAll = False
		self.numNotation = True


	def expand_all(self):
		self.expandAll = not self.expandAll


	def change_notation(self):
		self.numNotation = not self.numNotation


class StatsViewerStateWidget(QWidget):

	def __init__(self, viewer_state=None, session=None):

		super(StatsViewerStateWidget, self).__init__()

		self.ui = load_ui('viewer_state.ui', self,
						  directory=os.path.dirname(__file__))

		self.viewer_state = viewer_state
		self._connections = autoconnect_callbacks_to_qt(self.viewer_state, self.ui)

class StatsDataViewer(DataViewer):
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
	_toolbar_cls: Toolbar
		The toolbar of the StatsDataViewer
	tools: array
		array of tool ids shown on the StatsDataViewer toolbar
	shortcut: char
		character that can toggle the tool from keyboard
	----------
    """
	LABEL = 'Statistics viewer'
	_state_cls = StatsViewerState
	_options_cls = StatsViewerStateWidget


	_toolbar_cls = BasicToolbar
	tools = ['home_tool', 'refresh', 'calc_tool', 'sort_tool', 'notation_tool', 'export_tool'] #  'expand_tool'


	def __init__(self, *args, **kwargs):
		'''
		initializes the StatsDataViewer
		'''
		super(StatsDataViewer, self).__init__(*args, **kwargs)

		self.xc = self.session.data_collection # xc is dc, or the DataCollection DO NOT USE dc VARIABLE! It will mess up the IPython Terminal as it already uses a dc refrence
		self.no_update = True
		#self.calculatedSubsetViewList = np.array(["Subset,Dataset,Component,Mean,Median,Minimum,Maximum,Sum"])
		#self.calculatedComponentViewList = np.array(["Subset,Dataset,Component,Mean,Median,Minimum,Maximum,Sum"])

		self.headings = ('Name', 'Mean', 'Median', 'Minimum', 'Maximum', 'Sum')
		# Set up dict for caching
		self.cache_stash = dict()
		self.isSci = True
		self.num_sigs = 3
		# Set up past selected items
		self.past_selected = []

		# # Set component_mode to false, default is subset mode
		self.component_mode = False

		# # These will only be true when the treeview has to switch between views and a
		# # Change has been made in the other
		self.updateSubsetSort = False
		self.updateComponentSort = False
		self.selected_indices = []

		# Set up tree widget item for the view
		self.subsetTree = QTreeWidget(self)
		self.subsetTree.setSelectionMode(QAbstractItemView.MultiSelection)
		self.subsetTree.setColumnCount(6)
		self.subsetTree.setColumnWidth(0, 300)
		self.subsetTree.header().setSortIndicator(1, 0)
		QTreeWidget.setHeaderLabels(self.subsetTree, self.headings)
		self.subsetTree.itemClicked.connect(self.check_status)
		self.sortBySubsets()

		#component view tree Widget
		self.componentTree = QTreeWidget()
		self.componentTree.setSelectionMode(QAbstractItemView.MultiSelection)
		self.componentTree.setColumnCount(6)
		self.componentTree.setColumnWidth(0, 300)
		self.componentTree.header().setSortIndicator(1, 0)
		QTreeWidget.setHeaderLabels(self.componentTree, self.headings)
		self.sortByComponents()

		#set up the tabs for each of the two tree views
		self.tabs = QTabWidget()
		self.tabs1 = self.subsetTree
		self.tabs2  = self.componentTree
		self.tabs.addTab(self.tabs1,"Subset View")
		self.tabs.addTab(self.tabs2,"Component View")
		self.setCentralWidget(self.tabs)


		# Set up dicts for row indices
		self.subset_dict = dict()
		self.component_dict = dict()
		self.selected_dict = dict()


		#keeps track of how much data and subsets are loaded in
		self.dc_count = len(self.xc)
		self.subset_count = len(self.xc.subset_groups)

		#store the data and subsets, if any in the viewer at creation
		self.data_names = self.xc.labels
		self.subset_names = self.subsetNames()

		self.subset_set = set()

		self.componentViewExportCache = set()
		self.subsetViewExportCache = set()

	def refresh(self):
		'''
		action connected to Refresh Tool, enables subsets that were previously
		uncalculable to be calculated once linked
		'''

		if self.tabs.currentIndex() == 0:
			# get list of grayed out subset components
			list = []
			subset_branch = self.subsetTree.invisibleRootItem().child(1)
			for subset_i in range (0, len(self.xc.subset_groups)):
				for data_i in range (0, len(self.xc)):
					for comp_i in range (0, len(self.xc[data_i].components)):
						if subset_branch.child(subset_i).child(data_i).child(comp_i).foreground(0) == QtGui.QBrush(Qt.gray):
							list.append(self.subsetTree.indexFromItem(subset_branch.child(subset_i).child(data_i).child(comp_i)))
						else:
							break # so it only checks one if comp isnt grayed out

			#checks if any of the disabled components are now linkable and re-enables it
			for index in range (0, len(list)):
				# Subsets
				data_i = list[index].parent().row()
				comp_i = list[index].row()
				subset_i = list[index].parent().parent().row()

				try:
					median_val = self.xc[data_i].compute_statistic('median', self.xc[data_i].subsets[subset_i].components[comp_i], subset_state=self.xc.subset_groups[subset_i].subset_state)
					self.subsetTree.itemFromIndex(list[index]).setForeground(0,QtGui.QBrush(Qt.black))
					#self.subsetTree.itemFromIndex(list[index]).setData(0,0)
					self.subsetTree.itemFromIndex(list[index]).setCheckState(0, 0)
				except:
					pass

		elif self.tabs.currentIndex() == 1:
			#print("tab")
			# get list of grayed out subset components
			list = []
			for data_i in range(0,len(self.xc)):
				for subset_i in range(0, len(self.xc[data_i].components)):
					for comp_i in range(0, len(self.xc.subset_groups) + 1):
						if self.componentTree.invisibleRootItem().child(data_i).child(subset_i).child(comp_i).foreground(0) == QtGui.QBrush(Qt.gray):
							list.append(self.componentTree.indexFromItem(self.componentTree.invisibleRootItem().child(data_i).child(subset_i).child(comp_i)))
						else:
							pass
			#checks if any of the disabled components are now linkable and re-enables it
			for index in range (0, len(list)):
				data_i = list[index].parent().parent().row()
				comp_i = list[index].parent().row()
				subset_i = list[index].row() - 1

				try:
					median_val = self.xc[data_i].compute_statistic('median', self.xc[data_i].subsets[subset_i].components[comp_i], subset_state=self.xc.subset_groups[subset_i].subset_state)
					self.componentTree.itemFromIndex(list[index]).setForeground(0,QtGui.QBrush(Qt.black))
					#self.subsetTree.itemFromIndex(list[index]).setData(0,0)
					self.componentTree.itemFromIndex(list[index]).setCheckState(0, 0)
				except:
					pass

	def register_to_hub(self, hub):
		'''
		connects the StatsDataViewer to Messages that listen for changes to
		the viewer

		@param hub: takes in a HubListener object that can be connected with a Message for listening for changes
		'''
		super(StatsDataViewer, self).register_to_hub(hub)
		hub.subscribe(self, DataCollectionMessage, handler=self.newDataAddedMessage)
		hub.subscribe(self, DataCollectionDeleteMessage, handler=self.dataDeleteMessage)
		hub.subscribe(self, SubsetCreateMessage, handler=self.subsetCreatedMessage)
		hub.subscribe(self, SubsetDeleteMessage, handler=self.subsetDeleteMessage)
		hub.subscribe(self, DataUpdateMessage, handler=self.dataUpdateMessage)
		hub.subscribe(self, SubsetUpdateMessage, handler=self.subsetUpdateMessage)
		hub.subscribe(self, EditSubsetMessage, handler=self.editSubsetMessage)

	def editSubsetMessage(self, message):
		'''
		Clears calculated subsets of edited subsets in the viewer so they
		can be recalculated

		@param message: Message given by the event, contains details about how it was triggered
		'''
		#print("edit detected")
		editedSubset = ''
		#the sender._edit_subset is a list that has only one element, but use for loop just in case
		#print(message.sender._edit_subset)
		for x in message.sender._edit_subset:
			editedSubset = x.label

		#print("subset name: " + str(editedSubset))
		if not editedSubset == '':
			#update the subset view
			list = []
			subset_branch = self.subsetTree.invisibleRootItem().child(1)
			#j = ''
			#grandparent = ''
			for subset_i in range (0, subset_branch.childCount()):
				subset_group = subset_branch.child(subset_i)
				if subset_branch.child(subset_i).data(0,0) == editedSubset:
					for data in range(0,subset_group.childCount()):
						for component in range(0,subset_group.child(data).childCount()):
							item = self.subsetTree.indexFromItem(subset_branch.child(subset_i).child(data).child(component))
							print(subset_group.child(data).child(component).data(0,0))
							print(self.subsetTree.itemFromIndex(item).data(1,0))
							print(self.subsetTree.itemFromIndex(item).data(2,0))
							if self.subsetTree.itemFromIndex(item).data(1,0) == None:
								print("empty")
								break # nothing is calculated, automatically updated
							elif subset_group.data(0,0) == editedSubset and self.subsetTree.itemFromIndex(item).data(1,0) != None:
								print("remove values")
								#item = self.subsetTree.indexFromItem(subset_branch.child(subset_i).child(data).child(component))

								data_i = item.parent().row()
								comp_i = item.row()
								subset_i = item.parent().parent().row()

								subset_label = self.xc[data_i].subsets[subset_i].label
								data_label = self.xc[data_i].label
								comp_label = self.xc[data_i].components[comp_i].label # add to the name array to build the table
								# Build the cache key
								cache_key = subset_label + data_label + comp_label

								self.cache_stash.pop(cache_key)
								for col in range(1,6):
									 self.subsetTree.itemFromIndex(item).setData(col,0,None)

			#update the component view
			ct = self.componentTree.invisibleRootItem()
			for d in range(0,ct.childCount()):
				for c in range(0, ct.child(d).childCount()):
					for s in range(0, ct.child(d).child(c).childCount()):
						item = self.componentTree.indexFromItem(self.componentTree.invisibleRootItem().child(d).child(c).child(s))
						if self.componentTree.itemFromIndex(item).data(1,0) == None:
							break
						elif ct.child(d).child(c).child(s).data(0,0) == editedSubset and self.componentTree.itemFromIndex(item).data(1,0) != None:
							data_i = item.parent().parent().row()
							comp_i = item.parent().row()
							subset_i = item.row() - 1

							subset_label = self.xc[data_i].subsets[subset_i].label
							data_label = self.xc[data_i].label
							comp_label = self.xc[data_i].components[comp_i].label

							# Build the cache key
							cache_key = subset_label + data_label + comp_label
							self.cache_stash.pop(cache_key)
							for col in range(1,6):
								 self.componentTree.itemFromIndex(item).setData(col,0,None)

	def check_status(self, item , col):
		'''
		Enables hierachial box checks and unchecks

		@param item: QTreewidgetItem that has been checked/unchecked
		@param col: Column number of the action
		'''

		if item.checkState(0):
			#print("checked")
			#if the data branch is selected, check everything under data branch
			self.check_status_helper(2, item)
		else:
			#print("unchecked")
			# 0 means to uncheck NOTE: This is different then checkState. 0 for checkState means it is checked
			self.check_status_helper(0, item)

	def check_status_helper(self, state, dataset):
		'''
		Helper method for check_status(self, item , col)

		@param state: Number representing whether the action was check/uncheck
		@param dataset: QTreewidgetItem that has been checked/unchecked
		'''
		dataset_count = dataset.childCount()
		for x in range(dataset_count):
			attribute_count = dataset.child(x).childCount()
			if not dataset.child(x).foreground(0) == QtGui.QBrush(Qt.gray):
				dataset.child(x).setCheckState(0,state)

			for y in range(attribute_count):
				sub_attribute_count = dataset.child(x).child(y).childCount()
				if not dataset.child(x).child(y).foreground(0) == QtGui.QBrush(Qt.gray):
					dataset.child(x).child(y).setCheckState(0,state)

				#Only the subset section of the tree should be able to reach here
				for z in range(sub_attribute_count):
					if not dataset.child(x).child(y).child(z).foreground(0) == QtGui.QBrush(Qt.gray):
						dataset.child(x).child(y).child(z).setCheckState(0,state)

	def subsetNames(self):
		'''
		returns the current list of subsets in the glue session
		'''
		new_names = []
		for x in self.xc.subset_groups:
			new_names.append(x.label)
		return np.array(new_names)

	def subsetUpdateMessage(self, message):
		'''
		Updates the attributes of the edited subset (glue's left side panel info - names and color)

		@param message: Message given by the event, contains details about how it was triggered
		'''

		index1 = str(message).index("Subset: ") + len("Subset: ")
		index2 = str(message).index(" (data: ")
		new_name = str(message)[index1:index2]

		new_names = self.subsetNames()
		new_names = np.array(new_names)
		old_name = np.setdiff1d(self.subset_names, new_names)
		#print(self.subset_names)

		#update both tree views
		self.subsetViewSubsetUpdateHelper(self.subsetTree.invisibleRootItem().child(1), old_name, new_name)
		self.componentViewSubsetUpdateHelper(self.componentTree.invisibleRootItem(), old_name, new_name)

		self.subset_names = self.subsetNames()

	def componentViewSubsetUpdateHelper(self, viewType, old_name, new_name):
		'''
		Updates the component view if a subset atrribute is changed

		@param viewType: the QTreeWidget Tree that is being modified (subsetTree,componentTree)
		@param old_name: old name of the edited subset
		@param new_name: new name of the edited subset
		'''
		#for subset view
		subset_branch = viewType
		child_count = subset_branch.childCount()
		if len(old_name) == 0:
			#the name has not changed, so changed color
			old_name = "name is the same"
			#print(old_name)
			#print(self.xc[0])

			referenceTree = self.subsetTree.invisibleRootItem().child(1)
			indexOfSubset = ''
			for i in range(referenceTree.childCount()):
				if referenceTree.child(i).data(0,0) == new_name:
					indexOfSubset = i
					break

			for i in range(child_count):
				component_count = subset_branch.child(i)
				for x in range(component_count.childCount()):
					data_groups = subset_branch.child(i).child(x)
					for y in range(data_groups.childCount()):
						if subset_branch.child(i).child(x).child(y).data(0,0) == new_name:
							subset_branch.child(i).child(x).child(y).setIcon(0, helpers.layer_icon(self.xc.subset_groups[indexOfSubset]))
							break
		else:
			#update the dataset name in the statsviewer
			old_name = old_name[0]
			#print("old Name:")
			#print(old_name)
			for i in range(child_count):
				component_count = subset_branch.child(i)
				for x in range(component_count.childCount()):
					data_groups = subset_branch.child(i).child(x)
					for y in range(data_groups.childCount()):
						#print(old_name)
						#print(subset_branch.child(i).child(x).data(0,0))
						if subset_branch.child(i).child(x).child(y).data(0,0) == old_name:
							subset_branch.child(i).child(x).child(y).setData(0,0, new_name)
							break

	def subsetViewSubsetUpdateHelper(self, viewType, old_name, new_name):
		'''
		Updates the subset view if a subset atrribute is changed

		@param viewType: the QTreeWidget Tree that is being modified (subsetTree,componentTree)
		@param old_name: old name of the edited subset
		@param new_name: new name of the edited subset
		'''
		#for subset view
		subset_branch = viewType
		child_count = subset_branch.childCount()
		if len(old_name) == 0:
			#the name has not changed, so changed color
			old_name = "name is the same"
			#print(old_name)
			#print(self.xc[0])
			for i in range(child_count):
				subset_branch.child(i).setIcon(0, helpers.layer_icon(self.xc.subset_groups[i]))
				component_count = subset_branch.child(i).childCount()
				for x in range(component_count):
					subset_branch.child(i).child(x).setIcon(0, helpers.layer_icon(self.xc.subset_groups[i]))
					sub_component = subset_branch.child(i).child(x).childCount()
					for y in range(sub_component): #only subset edits reach here
						subset_branch.child(i).child(x).child(y).setIcon(0, helpers.layer_icon(self.xc.subset_groups[i]))
		else:
			#update the dataset name in the statsviewer
			old_name = old_name[0]
			#print("old Name:")
			#print(old_name)
			for i in range(child_count):
				component_count = subset_branch.child(i).childCount()
				if subset_branch.child(i).data(0,0) == old_name:
					subset_branch.child(i).setData(0,0, new_name)
					for x in range(component_count):
						#print(old_name)
						#print(subset_branch.child(i).child(x).data(0,0))
						if str(old_name) in str(subset_branch.child(i).child(x).data(0,0)):
							#print("asdf")
							new_label = str(subset_branch.child(i).child(x).data(0,0)).replace(str(old_name),str(new_name))
							subset_branch.child(i).child(x).setData(0,0,new_label)

	def dataUpdateMessage(self, message):
		'''
		Updates the attributes of the edited dataset (glue's left side panel info - names and color)

		@param message: Message given by the event, contains details about how it was triggered
		'''
		#print(message)

		# For subset view
		#first section of changing name
		index1 = str(message).index("Data Set: ") + len("Data Set: ")
		index2 = str(message).index("Number of dimensions: ") - 1
		new_name = str(message)[index1:index2]

		new_names = self.xc.labels
		old_name = np.setdiff1d(self.data_names, new_names)

		#update both views
		self.subsetViewDataUpdateHelper(self.subsetTree.invisibleRootItem().child(0), old_name, new_name)
		self.componentViewDataUpdateHelper(self.componentTree.invisibleRootItem(), old_name, new_name)
		#print(new_names)
		#print(self.data_names)
		#print(old_name)

		self.data_names = self.xc.labels

	def subsetViewDataUpdateHelper(self, viewType, old_name, new_name):
		'''
		Updates the subset view if a data atrribute is changed

		@param viewType: the QTreeWidget Tree that is being modified (subsetTree,componentTree)
		@param old_name: old name of the edited subset
		@param new_name: new name of the edited subset
		'''
		data_branch = viewType
		child_count = data_branch.childCount()
		#print("aaa")
		if len(old_name) == 0:
			#the name has not changed, so changed color
			#print("bbb")
			old_name = "name is the same"
			for i in range(child_count):
				data_branch.child(i).setIcon(0, helpers.layer_icon(self.xc[i]))
				component_count = data_branch.child(i).childCount()
				for x in range(component_count):
					data_branch.child(i).child(x).setIcon(0, helpers.layer_icon(self.xc[i]))
		else:
			#update the dataset name in the statsviewer
			#print('aaa')
			old_name = old_name[0]
			print(old_name)
			for i in range(child_count):
				if data_branch.child(i).data(0,0) == old_name:
					data_branch.child(i).setData(0,0, new_name)

			#update the subsets that contain the old name, if any
			if len(self.xc.subset_groups) != 0:
				print(old_name)
				print(new_name)
				subset_branch = self.subsetTree.invisibleRootItem().child(1)
				child_count = subset_branch.childCount()
				for i in range(child_count):
					component_count = subset_branch.child(i).childCount()
					for x in range(component_count):
						#print(old_name)
						#print(subset_branch.child(i).child(x).data(0,0))
						if "(" + str(old_name) + ")" in str(subset_branch.child(i).child(x).data(0,0)):
							new_label = str(subset_branch.child(i).child(x).data(0,0)).replace(str(old_name),str(new_name))
							subset_branch.child(i).child(x).setData(0,0,new_label)

	def componentViewDataUpdateHelper(self, viewType, old_name, new_name):
		'''
		Updates the component view if a data atrribute is changed

		@param viewType: the QTreeWidget Tree that is being modified (subsetTree,componentTree)
		@param old_name: old name of the edited subset
		@param new_name: new name of the edited subset
		'''
		data_branch = viewType
		child_count = data_branch.childCount()
		#print("aaa")
		if len(old_name) == 0:
			#the name has not changed, so changed color
			#print("bbb")
			old_name = "name is the same"

			referenceTree = self.subsetTree.invisibleRootItem().child(0)
			indexOfSubset = ''
			for i in range(referenceTree.childCount()):
				if referenceTree.child(i).data(0,0) == new_name:
					indexOfSubset = i
					break
			#print(indexOfSubset)
			#for i in range(child_count): # data
			#	component_count = data_branch.child(i)
			#	if data_branch.child(i).data(0,0) == new_name:

			for i in range(child_count):
				component_count = data_branch.child(i).childCount()
				if data_branch.child(i).data(0,0) == new_name:
					data_branch.child(i).setIcon(0, helpers.layer_icon(self.xc[indexOfSubset]))
				for x in range(component_count):
					#data_branch.child(i).child(x).setIcon(0, helpers.layer_icon(self.xc.subset_groups[indexOfSubset]))
					data_groups = data_branch.child(i).child(x)
					for y in range(data_groups.childCount()):
						if "(" + str(new_name) + ")" in str(data_branch.child(i).child(x).child(y).data(0,0)):
							data_branch.child(i).child(x).child(y).setIcon(0, helpers.layer_icon(self.xc[indexOfSubset]))
							break
		else:
			#update the dataset name in the statsviewer
			#print('aaa')
			old_name = old_name[0]
			#print(old_name)

			for i in range(child_count): # data
				component_count = data_branch.child(i)
				if data_branch.child(i).data(0,0) == old_name:
					data_branch.child(i).setData(0,0, new_name)
				for x in range(component_count.childCount()):
					data_groups = data_branch.child(i).child(x)
					for y in range(data_groups.childCount()):
						if "(" + str(old_name) + ")" in str(data_branch.child(i).child(x).child(y).data(0,0)):
							new_label = str(data_branch.child(i).child(x).child(y).data(0,0)).replace(str(old_name),str(new_name))
							data_branch.child(i).child(x).child(y).setData(0,0,new_label)
							break


		'''	#update the subsets that contain the old name, if any
			if len(self.xc.subset_groups) != 0:
				print(old_name)
				print(new_name)
				subset_branch = self.subsetTree.invisibleRootItem().child(1)
				child_count = subset_branch.childCount()
				for i in range(child_count):
					component_count = subset_branch.child(i).childCount()
					for x in range(component_count):
						#print(old_name)
						#print(subset_branch.child(i).child(x).data(0,0))
						if "(" + str(old_name) + ")" in str(subset_branch.child(i).child(x).data(0,0)):
							new_label = str(subset_branch.child(i).child(x).data(0,0)).replace(str(old_name),str(new_name))
							subset_branch.child(i).child(x).setData(0,0,new_label)'''

	def newDataAddedMessage(self, message):
		'''
		Adds a new dataset to the viewer

		@param message: Message given by the event, contains details about how it was triggered
		'''
		#print("detected new data added")

		'''For subset view'''
		parentItem = QTreeWidgetItem(self.dataItem)
		parentItem.setCheckState(0, 0)
		i = self.dc_count
		parentItem.setData(0, 0, '{}'.format(self.xc.labels[i]))
		parentItem.setIcon(0, helpers.layer_icon(self.xc[i]))

		# Make all the data components be children, nested under their parent
		for j in range(0,len(self.xc[i].components)):

			childItem = QTreeWidgetItem(parentItem)
			childItem.setCheckState(0, 0)
			childItem.setData(0, 0, '{}'.format(str(self.xc[i].components[j])))
			childItem.setIcon(0, helpers.layer_icon(self.xc[i]))

			# Add to the subset_dict
			key = self.xc[i].label + self.xc[i].components[j].label + "All data-" + self.xc[i].label
			self.num_rows = self.num_rows + 1

		'''For component view'''
		grandparent = QTreeWidgetItem(self.componentTree)
		grandparent.setData(0, 0, '{}'.format(self.xc.labels[i]))
		grandparent.setIcon(0, helpers.layer_icon(self.xc[i]))
		grandparent.setCheckState(0, 0)

		for k in range(0,len(self.xc[i].components)):
			parent = QTreeWidgetItem(grandparent)
			parent.setData(0, 0, '{}'.format(str(self.xc[i].components[k])))
			parent.setCheckState(0, 0)

			child = QTreeWidgetItem(parent)
			child.setData(0, 0, '{}'.format('All data (' + self.xc.labels[i] + ')'))
			child.setIcon(0, helpers.layer_icon(self.xc[i]))
			child.setCheckState(0, 0)

			self.num_rows = self.num_rows + 1
			disableSubset = False
			temp = False

			for j in range(0, len(self.xc.subset_groups)):
				childtwo = QTreeWidgetItem(parent)
				childtwo.setData(0, 0, '{}'.format(self.xc.subset_groups[j].label))
				# child.setEditable(False)
				childtwo.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
				childtwo.setCheckState(0, 0)

				if (not disableSubset) and (not temp):
					try:
						 self.xc[i].compute_statistic('minimum', self.xc[i].subsets[j].components[k], subset_state=self.xc.subset_groups[j].subset_state)
						 temp = True
					except:
						disableSubset = True
				if disableSubset:
					childtwo.setData(0, Qt.CheckStateRole, QVariant())
					childtwo.setForeground(0,QtGui.QBrush(Qt.gray))
				self.num_rows = self.num_rows + 1

		self.dc_count += 1
		self.data_names = self.xc.labels

	def subsetCreatedMessage(self, message):
		'''
		Adds a new subset to the viewer

		@param message: Message given by the event, contains details about how it was triggered
		'''

		#print("detected new subset creation")
		#print(message)

		index1 = str(message).index("Subset: ") + len("Subset: ")
		index2 = str(message).index(" (data: ")
		current_subset = str(message)[index1:index2]
		#print(current_subset)

		#For subset view

		if not current_subset in self.subset_set:
		#if not current_subset in self.subset_dict:

			j = self.subset_count
			grandparent = QTreeWidgetItem(self.subsetItem)
			grandparent.setData(0, 0, '{}'.format(self.xc.subset_groups[j].label))
			grandparent.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
			grandparent.setCheckState(0, 0)
			count = 0
			for i in range(0, len(self.xc)):
				count = i+1
				parent = QTreeWidgetItem(grandparent)
				parent.setData(0, 0, '{}'.format(self.xc.subset_groups[j].label) + ' (' + '{}'.format(self.xc[i].label) + ')')
				parent.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
				parent.setCheckState(0, 0)

				disableSubset = False
				temp = False
				for k in range(0, len(self.xc[i].components)):
					child = QTreeWidgetItem(parent)
					child.setData(0, 0, '{}'.format(str(self.xc[i].components[k])))
					child.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
					child.setCheckState(0, 0)

					if (not disableSubset) and (not temp):
						try:
							 self.xc[i].compute_statistic('minimum', self.xc[i].subsets[j].components[k], subset_state=self.xc.subset_groups[j].subset_state)
							 #self.xc[i].compute_statistic('minimum', self.dc[i].subsets[j].components[k], subset_state=self.dc[i].subsets[j].subset_state)
							 temp = True
						except:
							#child.setData(0, Qt.CheckStateRole, QVariant())
							disableSubset = True
					if disableSubset:
						child.setData(0, Qt.CheckStateRole, QVariant())
						child.setForeground(0,QtGui.QBrush(Qt.gray))

					self.num_rows = self.num_rows + 1



			'''Component View'''
			for i in range(0,self.componentTree.invisibleRootItem().childCount()):
				parent = self.componentTree.invisibleRootItem().child(i)
				disableSubset = False
				temp = False
				for k in range(0,parent.childCount()):
					component = parent.child(k)
					disableSubset = False
					temp = False

					childtwo = QTreeWidgetItem(component)
					childtwo.setData(0, 0, '{}'.format(current_subset))
					# child.setEditable(False)
					childtwo.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
					childtwo.setCheckState(0, 0)

					if (not disableSubset) and (not temp):
						try:
							 self.xc[i].compute_statistic('minimum', self.xc[i].subsets[j].components[k], subset_state=self.xc.subset_groups[j].subset_state)
							 #self.xc[i].compute_statistic('minimum', self.dc[i].subsets[j].components[k], subset_state=self.dc[i].subsets[j].subset_state)
							 temp = True
						except:
							#child.setData(0, Qt.CheckStateRole, QVariant())
							disableSubset = True
					if disableSubset:
						childtwo.setData(0, Qt.CheckStateRole, QVariant())
						childtwo.setForeground(0,QtGui.QBrush(Qt.gray))
			self.subset_set.add(current_subset)
			#self.subset_dict.update({current_subset : count})
			self.subset_count += 1
			#self.subset_dict.update({current_subset:self.dc_count})
			#print("dict: "+ str(self.subset_dict.get(current_subset)))
			#print("dc count:" + str(self.dc_count))

			#if new sub-subset needs to be added


	def dataDeleteMessage(self,message):
		'''
		Removes deleted dataset from the viewer

		@param message: Message given by the event, contains details about how it was triggered
		'''
		print("detected data removal")
		print(message)
		self.deleteHelper('dataset')
		self.dc_count -= 1

	def subsetDeleteMessage(self, message):
		'''
		Removes deleted subset from the viewer

		@param message: Message given by the event, contains details about how it was triggered
		'''
		#print("detected subset deletion")
		self.deleteHelper('subset')
		self.subset_count -= 1

	def deleteHelper(self, deletedType):
		'''
		Helper method for dataDeleteMessage(self,message) and subsetDeleteMessage(self, message)

		@param message: Message given by the event, contains details about how it was triggered
		'''
		#print(deletedType)
		current_list = np.array([])
		past_list = np.array([])
		temp = -1
		if deletedType == 'dataset':
			temp = 0
			#creates a list of the current values in the data_collection
			for ds in self.xc:
				current_list = np.append(current_list, ds.label)
		if deletedType == 'subset':
			temp = 1
			current_list = self.subsetNames()

		if temp == -1:
			print("invalid delete code")

		'''Subset view'''
		#data branch of tree
		data_branch = self.subsetTree.invisibleRootItem().child(temp)
		#counts the number of each dataset
		child_count = data_branch.childCount()
		#creates a list of the values in the outdated tree
		for i in range(child_count):
			past_list = np.append(past_list, data_branch.child(i).data(0,0))
		#print(current_list)
		#print(past_list)
		#print(np.setdiff1d(past_list, current_list)[0])
		removalList = np.setdiff1d(past_list, current_list)
		if len(removalList) != 0:
			toBeRemoved = np.setdiff1d(past_list, current_list)[0]
			toBeRemovedQItem = ''
			for i in range(child_count):
				if data_branch.child(i).data(0,0) == toBeRemoved:
					toBeRemovedQItem = data_branch.child(i)
			data_branch.removeChild(toBeRemovedQItem)
			#print(self.subset_set)
			if deletedType == 'subset':
				#self.subset_set.remove(str(toBeRemoved))
				self.subset_dict.pop(str(toBeRemoved))
			#print(self.subset_set)

		'''Component View'''
		#data branch of tree
		data_branch = self.componentTree.invisibleRootItem()
		#counts the number of each dataset
		child_count = data_branch.childCount()
		#creates a list of the values in the outdated tree
		for i in range(child_count):
			past_list = np.append(past_list, data_branch.child(i).data(0,0))
		#print(current_list)
		#print(past_list)
		#print(np.setdiff1d(past_list, current_list)[0])
		removalList = np.setdiff1d(past_list, current_list)
		if len(removalList) != 0:
			toBeRemoved = np.setdiff1d(past_list, current_list)[0]
			toBeRemovedQItem = ''
			for i in range(child_count):
				if data_branch.child(i).data(0,0) == toBeRemoved:
					toBeRemovedQItem = data_branch.child(i)
			data_branch.removeChild(toBeRemovedQItem)
			#print(self.subset_set)
			if deletedType == 'subset':
				#self.subset_set.remove(str(toBeRemoved))
				self.subset_dict.pop(str(toBeRemoved))

	def initialize_toolbar(self):
		'''
		Initializes the the toolbar: add any further customizations here
		'''
		super(StatsDataViewer, self).initialize_toolbar()
		BasicToolbar.setContextMenuPolicy(self,Qt.PreventContextMenu)

	def myPressedEvent(self, currentQModelIndex):
		pass

	def expandAll(self, bool):

		item_List = self.past_itemMasterList

		for qtwitem in item_List:
			qtwitem.setExpanded(bool)

	def pressedEventCalculate(self, sciFi):

		'''
		Calculates stats for the rows that are checked
		'''
		'''
		Every time the selection in the treeview changes:
		if it is newly selected, add it to the table
		if it is newly deselected, remove it from the table
		'''

		self.selected_indices = []


		# create list of rows to calculate
		if self.tabs.currentIndex() == 0 :
			data_branch = self.subsetTree.invisibleRootItem().child(0)
			for data_i in range (0, len(self.xc)):

				for comp_i in range (0, len(self.xc[data_i].components)):

					# if checked, add to selected list
					if data_branch.child(data_i).child(comp_i).checkState(0): #or self.nestedtree.invisibleRootItem().child(0).child(data_i).checkState(0) or self.nestedtree.invisibleRootItem().child(0).checkState(0):
						self.selected_indices.append(
							self.subsetTree.indexFromItem(data_branch.child(data_i).child(comp_i)))
					else:
						pass
			subset_branch = self.subsetTree.invisibleRootItem().child(1)
			for subset_i in range (0, len(self.xc.subset_groups)):
				#print("subset: "+ str(subset_i))
				for data_i in range (0, len(self.xc)):
					#print("dataset: "+ str(data_i))
					for comp_i in range (0, len(self.xc[data_i].components)):
						#print("component: "+ str(comp_i))
						try:
							if subset_branch.child(subset_i).child(data_i).child(comp_i).checkState(0):# or self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).child(subset_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).checkState(0):
								#print("lalalal")
								self.selected_indices.append(
									self.subsetTree.indexFromItem(subset_branch.child(subset_i).child(data_i).child(comp_i)))
						except:
							pass

		else:
			for data_i in range(0,len(self.xc)):

				# subset_i and comp_i are switched by accident
				for subset_i in range(0, len(self.xc[data_i].components)):

					for comp_i in range(0, len(self.xc.subset_groups) + 1):

						if self.componentTree.invisibleRootItem().child(data_i).child(subset_i).child(comp_i).checkState(0): # or self.nestedtree.invisibleRootItem().child(data_i).child(subset_i).checkState(0) or self.nestedtree.invisibleRootItem().child(data_i).checkState(0):
							self.selected_indices.append(
								self.componentTree.indexFromItem(self.componentTree.invisibleRootItem().child(data_i).child(subset_i).child(comp_i)))
						else :
							pass

		newly_selected = np.setdiff1d(self.selected_indices, self.past_selected)
		#print(self.selected_indices)
		#print("xaxaxaxa")
		#print(self.selected_indices[0])
		for index in range (0, len(newly_selected)):

			# Check which view mode the tree is in to get the correct indices
			#if the current tab is in subset view
			if self.tabs.currentIndex() == 0:

				if newly_selected[index].parent().parent().parent().row() == -1:
					# Whole data sets
					data_i = newly_selected[index].parent().row()
					comp_i = newly_selected[index].row()
					subset_i = -1
				else:
					# Subsets
					data_i = newly_selected[index].parent().row()
					comp_i = newly_selected[index].row()
					subset_i = newly_selected[index].parent().parent().row()
			#if the current tab is in component view
			else:
				data_i = newly_selected[index].parent().parent().row()
				comp_i = newly_selected[index].parent().row()
				subset_i = newly_selected[index].row() - 1

			is_subset = (subset_i != -1)

			# Check if its a subset and if so run subset stats
			if is_subset:
				new_data = self.runSubsetStats(subset_i, data_i, comp_i)

			else:
				# Run standard data stats
				new_data = self.runDataStats(data_i, comp_i)

			#print(new_data)
			#print("xoxoxo")
			#print(newly_selected[index].row())
			#print("newly selected item ^")
			#print(self.nestedtree.itemFromIndex(newly_selected[index]))
			#print(new_data[0])
			#print(new_data[1])
			#print(new_data[2])
			# self.nestedtree.itemFromIndex(newly_selected[0]).setData(0, 0, new_data[0][0])
			'''cache_key = new_data[0] + new_data[1] + new_data[2]
			temp = ''
			if self.tabs.currentIndex() == 0 and not cache_key in self.subsetViewExportCache:
				temp = 'subset'
				self.subsetViewExportCache.add(cache_key)
			elif self.tabs.currentIndex() == 1 and not cache_key in self.componentViewExportCache:
				temp = 'component'
				self.componentViewExportCache.add(cache_key)
			if not temp == '':'''
			for col_index in range (0, len(new_data)):
				if not sciFi:
					if self.tabs.currentIndex() == 0:
						self.calculatedSubsetViewList = np.append(self.calculatedSubsetViewList, new_data[col_index])
					elif self.tabs.currentIndex() == 1:
						self.calculatedComponentViewList = np.append(self.calculatedComponentViewList, new_data[col_index])

				if (col_index > 2):
					#print(new_data[col_index])
					if self.tabs.currentIndex() == 0:
						self.subsetTree.itemFromIndex(newly_selected[index]).setData(col_index-2, 0, new_data[col_index])
					elif self.tabs.currentIndex() == 1:
						self.componentTree.itemFromIndex(newly_selected[index]).setData(col_index-2, 0, new_data[col_index])

	def getCurrentCalculated(self):
		'''
		returns list of current calculated values in the current opened viewer
		'''
		currentCalculated = -1
		if self.tabs.currentIndex() == 0:
			currentCalculated = np.array(["Subset,Dataset,Component,Mean,Median,Minimum,Maximum,Sum"])
			#data
			st = self.subsetTree.invisibleRootItem().child(0)
			for x in range(0,st.childCount()):
				for y in range(0, st.child(x).childCount()):
					item = self.subsetTree.indexFromItem(st.child(x).child(y))
					if self.subsetTree.itemFromIndex(item).data(3,0) != None:
						currentCalculated = np.append(currentCalculated, '--') # no subset
						currentCalculated = np.append(currentCalculated, st.child(x).data(0,0)) # dataset
						for t in range(0, 6):
							currentCalculated = np.append(currentCalculated, self.subsetTree.itemFromIndex(item).data(t,0))
			#subset
			st = self.subsetTree.invisibleRootItem().child(1)
			for x in range(0,st.childCount()):
				for y in range(0, st.child(x).childCount()):
					for z in range(0,st.child(x).child(y).childCount()):
						item = self.subsetTree.indexFromItem(st.child(x).child(y).child(z))
						if self.subsetTree.itemFromIndex(item).data(3,0) != None:
							currentCalculated = np.append(currentCalculated, st.child(x).child(y).data(0,0)) #subset(data) name
							temp = str(st.child(x).child(y).data(0,0))
							index1 = temp.index("(")+1
							index2 = temp.index(")")
							dataset_name = temp[index1:index2]
							currentCalculated = np.append(currentCalculated, dataset_name) #dataset name
							for t in range(0, 6):
								currentCalculated = np.append(currentCalculated, self.subsetTree.itemFromIndex(item).data(t,0))

		elif self.tabs.currentIndex() == 1:
			currentCalculated = np.array(["Dataset,Component,Subset,Mean,Median,Minimum,Maximum,Sum"])
			ct = self.componentTree.invisibleRootItem()
			for x in range(0,ct.childCount()):
				for y in range(0, ct.child(x).childCount()):
					for z in range(0,ct.child(x).child(y).childCount()):
						item = self.componentTree.indexFromItem(ct.child(x).child(y).child(z))
						if self.componentTree.itemFromIndex(item).data(3,0) != None:
							currentCalculated = np.append(currentCalculated, ct.child(x).data(0,0)) #dataset
							currentCalculated = np.append(currentCalculated, ct.child(x).child(y).data(0,0)) #component
							for t in range(0, 6):
								currentCalculated = np.append(currentCalculated, self.componentTree.itemFromIndex(item).data(t,0))

		return currentCalculated


	def pressedEventExport(self):
		'''
		Exports the current calculated values of the tab that is open
		'''
		df = self.getCurrentCalculated()
		file_name, fltr = compat.getsavefilename(caption="Choose an output filename")
		try:
			df = pd.DataFrame(df)
			df.to_csv(str(file_name), header=None ,index=None)
		except:
			print("Export failed ")

	def pressedEventConvertNotation(self, bool):
		'''
		Converts from scientific to decimal and vice versa
		'''
		self.isSci = bool

		# recalculate with new notation,
		# data is cached already so it should be quick
		self.pressedEventCalculate(True)

	def decPlaces(self, intDecimal):
		'''
		Changes num_sigs to the given int and updates the tree appropriatelt
		'''
		item_List = self.itemMasterList()

		# list of current checked items so that we can re'check' them later
		checked_list = []

		uncheck_list = []

		for qtwitem in item_List:
			# currentItem = self.nestedtree.itemFromIndex(qtwitem)

			# if its checked
			if qtwitem.checkState(0):
				checked_list.append(qtwitem)

			# if it has data, check it so it can be recalculated
			if qtwitem.data(1, 0) is None:
				qtwitem.setCheckState(0, 0)
			else:
				qtwitem.setCheckState(0, 2)
				uncheck_list.append(qtwitem)

		#print(checked_list)

		self.num_sigs = intDecimal
		#print("decimal changed")

		# self.expandAll(True)
		# print("expanded")

		# recalculate with new notation,
		# data is cached already so it should be quick
		self.pressedEventCalculate(True)

		# uncheck everything
		for qtwitem in uncheck_list:
			qtwitem.setCheckState(0, 0)

		# recheck checked list items
		for qtwitem in checked_list:
			qtwitem.setCheckState(0, 2)

	def runDataStats (self, data_i, comp_i):
		'''
		Runs statistics for the component comp_i of data set data_i

		@param data_i: data index from the tree
		@param comp_i: component index from the tree
		'''

		subset_label = "--"
		data_label = self.xc[data_i].label
		comp_label = self.xc[data_i].components[comp_i].label # add to the name array to build the table

		#print("hihihi")
		#print(data_label)
		#print(comp_label)
		# Build the cache key
		cache_key = subset_label + data_label + comp_label

		#print(cache_key)
		# See if the values have already been cached
		if True: # self.noupdate
			try:
				column_data = self.cache_stash[cache_key]
			except:
				column_data = self.newDataStats(data_i, comp_i)
		else:
			column_data = self.newDataStats(data_i, comp_i)
		#print(column_data)
		# Save the accurate data in self.data_accurate
		# column_df = pd.DataFrame(column_data, columns=self.headings)
		# self.data_accurate = self.data_accurate.append(column_df, ignore_index=True)

		if self.isSci:
			# Format in scientific notation
			string = "%." + str(self.num_sigs) + 'E'
		else:
			# Format in standard notation
			string = "%." + str(self.num_sigs) + 'F'

		#print("xxyyzz")
		#print(string)

		mean_val = string % column_data[3]
		#print(mean_val)
		#print("mean_val ^^")
		median_val = string % column_data[4]
		min_val = string % column_data[5]
		max_val = string % column_data[6]
		sum_val = string % column_data[7]


		# DAN - I'm choosing to get rid of the df (DataFrame) since we no longer have two tables, only one
		# I'm instead making this retrn the column_data and putting it directly into the table.

		# Create the column data array and append it to the data frame
		column_data = (subset_label, data_label, comp_label, mean_val, median_val, min_val, max_val, sum_val)
		# column_df = pd.DataFrame(column_data, columns=self.headings)
		# # self.data_frame = self.data_frame.append(column_df, ignore_index=True)
		return column_data

	def newDataStats(self, data_i, comp_i):
		'''
		Runs statistics for the component comp_i of data set data_i

		@param data_i: data index from the tree
		@param comp_i: component index from the tree
		'''
		#print("newDataStats triggered")
		# Generates new data for a dataset that has to be calculated

		subset_label = "--"
		data_label = self.xc[data_i].label
		comp_label = self.xc[data_i].components[comp_i].label # add to the name array to build the table

		# Build the cache key
		cache_key = subset_label + data_label + comp_label

		# Find the stat values
		# Save the data in the cache
		mean_val = self.xc[data_i].compute_statistic('mean', self.xc[data_i].components[comp_i])
		median_val = self.xc[data_i].compute_statistic('median', self.xc[data_i].components[comp_i])
		min_val = self.xc[data_i].compute_statistic('minimum', self.xc[data_i].components[comp_i])
		max_val = self.xc[data_i].compute_statistic('maximum', self.xc[data_i].components[comp_i])
		sum_val = self.xc[data_i].compute_statistic('sum', self.xc[data_i].components[comp_i])

		column_data = (subset_label, data_label, comp_label, mean_val, median_val, min_val, max_val, sum_val)

		self.cache_stash[cache_key] = column_data

		return column_data

	def runSubsetStats (self, subset_i, data_i, comp_i):
		'''
		Runs statistics for the subset subset_i with respect to the component comp_i of data set data_i

		@param subset_i: subset index from tree
		@param data_i: data index from the tree
		@param comp_i: component index from the tree

		'''

		subset_label = self.xc[data_i].subsets[subset_i].label
		data_label = self.xc[data_i].label
		comp_label = self.xc[data_i].components[comp_i].label # add to the name array to build the table

		# Build the cache key
		cache_key = subset_label + data_label + comp_label

		# See if the statistics are already in the cache if nothing needs to be updated

		if True:
			try:
				column_data = self.cache_stash[cache_key]
			except:
				column_data = self.newSubsetStats(subset_i, data_i, comp_i)
		else:
			column_data = self.newSubsetStats(subset_i, data_i, comp_i)

		if self.isSci:
			# Format in scientific notation
			string = "%." + str(self.num_sigs) + 'E'
		else:
			# Format in standard notation
			string = "%." + str(self.num_sigs) + 'F'

		mean_val = string % column_data[3]
		#print(mean_val)
		#print("mean_val ^")
		median_val = string % column_data[4]
		min_val = string % column_data[5]
		max_val = string % column_data[6]
		sum_val = string % column_data[7]

		# Create the column data array and append it to the data frame
		column_data = (subset_label, data_label, comp_label, mean_val, median_val, min_val, max_val, sum_val)
		return column_data

	def newSubsetStats(self, subset_i, data_i, comp_i):

		'''
		Runs statistics for the subset subset_i with respect to the component comp_i of data set data_i

		@param subset_i: subset index from tree
		@param data_i: data index from the tree
		@param comp_i: component index from the tree

		'''
		# Generates new data for a subset that needs to be calculated
		subset_label = self.xc[data_i].subsets[subset_i].label
		data_label = self.xc[data_i].label
		comp_label = self.xc[data_i].components[comp_i].label # add to the name array to build the table

		# Build the cache key
		cache_key = subset_label + data_label + comp_label

		mean_val = self.xc[data_i].compute_statistic('mean', self.xc[data_i].subsets[subset_i].components[comp_i], subset_state=self.xc[data_i].subsets[subset_i].subset_state)
		median_val = self.xc[data_i].compute_statistic('median', self.xc[data_i].subsets[subset_i].components[comp_i], subset_state=self.xc.subset_groups[subset_i].subset_state)
		min_val = self.xc[data_i].compute_statistic('minimum', self.xc[data_i].subsets[subset_i].components[comp_i], subset_state=self.xc.subset_groups[subset_i].subset_state)
		max_val = self.xc[data_i].compute_statistic('maximum', self.xc[data_i].subsets[subset_i].components[comp_i], subset_state=self.xc.subset_groups[subset_i].subset_state)
		sum_val = self.xc[data_i].compute_statistic('sum', self.xc[data_i].subsets[subset_i].components[comp_i], subset_state=self.xc.subset_groups[subset_i].subset_state)

		column_data = (subset_label, data_label, comp_label, mean_val, median_val, min_val, max_val, sum_val)

		self.cache_stash[cache_key] = column_data

		return column_data

	def mousePressEvent(self, event):
		pass

	def sortBySubsets(self):
		'''
		Sorts the treeview by subsets- Dataset then subset then component.
		What we originally had as the default
		'''
		# Set to not component mode
		self.component_mode = False

		# Clear the num_rows
		self.num_rows = 0

		# Clear the data_accurate
		self.data_accurate = pd.DataFrame(columns=self.headings)



		# Clear the selection
		self.subsetTree.clearSelection()

		# Clear the tree
		self.subsetTree.clear()

		#Allow the user to select multiple rows at a time
		self.selection_model = QAbstractItemView.MultiSelection
		self.subsetTree.setSelectionMode(self.selection_model)


		self.subsetTree.setUniformRowHeights(True)

		self.generateSubsetView()
		# self.nestedtree.header.moveSection(1, 0)

		# Make the table update whenever the selection in the tree is changed
		selection_model = QItemSelectionModel(self.model_subsets)
		#self.nestedtree.setSelectionModel(selection_model)
		selection_model.selectionChanged.connect(self.myPressedEvent)
		self.subsetTree.itemClicked.connect(self.check_status)


	def generateSubsetView(self):
		'''
		Creates the subset view for the viewer
		'''
		#self.component_mode = False
		self.model_subsets = QStandardItemModel()
		self.model_subsets.setHorizontalHeaderLabels([''])

		self.dataItem =  QTreeWidgetItem(self.subsetTree)
		self.dataItem.setData(0, 0, '{}'.format('Data'))
		# dataItem.setExpanded(True)
		self.dataItem.setCheckState(0, 0)


		for i in range(0, len(self.xc)):

			parentItem = QTreeWidgetItem(self.dataItem)
			parentItem.setCheckState(0, 0)
			parentItem.setData(0, 0, '{}'.format(self.xc.labels[i]))
			parentItem.setIcon(0, helpers.layer_icon(self.xc[i]))

			# Make all the data components be children, nested under their parent
			for j in range(0,len(self.xc[i].components)):

				childItem = QTreeWidgetItem(parentItem)
				childItem.setCheckState(0, 0)
				childItem.setData(0, 0, '{}'.format(str(self.xc[i].components[j])))
				childItem.setIcon(0, helpers.layer_icon(self.xc[i]))

				# Add to the subset_dict
				key = self.xc[i].label + self.xc[i].components[j].label + "All data-" + self.xc[i].label


				self.num_rows = self.num_rows + 1



		self.subsetItem = QTreeWidgetItem(self.subsetTree)
		self.subsetItem.setData(0, 0, '{}'.format('Subsets'))
		self.subsetItem.setCheckState(0, 0)

		for j in range(0, len(self.xc.subset_groups)):

			grandparent = QTreeWidgetItem(self.subsetItem)
			grandparent.setData(0, 0, '{}'.format(self.xc.subset_groups[j].label))
			grandparent.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
			grandparent.setCheckState(0, 0)

			for i in range(0, len(self.xc)):

				parent = QTreeWidgetItem(grandparent)
				parent.setData(0, 0, '{}'.format(self.xc.subset_groups[j].label) + ' (' + '{}'.format(self.xc[i].label) + ')')

				parent.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
				parent.setCheckState(0, 0)

				disableSubset = False
				temp = False

				for k in range(0, len(self.xc[i].components)):

					child = QTreeWidgetItem(parent)
					child.setData(0, 0, '{}'.format(str(self.xc[i].components[k])))
					#child.setEditable(False)
					child.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
					child.setCheckState(0, 0)

					if (not disableSubset) and (not temp):
						try:
							 self.xc[i].compute_statistic('minimum', self.xc[i].subsets[j].components[k], subset_state=self.xc.subset_groups[j].subset_state)
							 #self.xc[i].compute_statistic('minimum', self.dc[i].subsets[j].components[k], subset_state=self.dc[i].subsets[j].subset_state)
							 temp = True
						except:
							#child.setData(0, Qt.CheckStateRole, QVariant())
							disableSubset = True
					if disableSubset:
						child.setData(0, Qt.CheckStateRole, QVariant())
						child.setForeground(0,QtGui.QBrush(Qt.gray))


					self.num_rows = self.num_rows + 1



		self.subsetTree.setUniformRowHeights(True)


	def sortByComponents(self):
		'''
		Sorts the treeview by components- Dataset then component then subsets
		'''
		# Set component_mode to true
		self.component_mode = True

		# Clear the num_rows
		self.num_rows = 0

		# Clear the data_accurate
		self.data_accurate = pd.DataFrame(columns=self.headings)

		# Clear the selection
		self.componentTree.clearSelection()
		self.componentTree.clear()


		self.selection_model = QAbstractItemView.MultiSelection
		self.componentTree.setSelectionMode(self.selection_model)


		self.generateComponentView()

		self.componentTree.setUniformRowHeights(True)
		self.componentTree.itemClicked.connect(self.check_status)


	def generateComponentView(self):
		'''
		Creates the component view for the viewer
		'''
		self.component_mode = True

		for i in range(0,len(self.xc)):

			grandparent = QTreeWidgetItem(self.componentTree)
			grandparent.setData(0, 0, '{}'.format(self.xc.labels[i]))
			grandparent.setIcon(0, helpers.layer_icon(self.xc[i]))
			grandparent.setCheckState(0, 0)

			for k in range(0,len(self.xc[i].components)):
				parent = QTreeWidgetItem(grandparent)
				parent.setData(0, 0, '{}'.format(str(self.xc[i].components[k])))
				parent.setCheckState(0, 0)

				child = QTreeWidgetItem(parent)
				child.setData(0, 0, '{}'.format('All data (' + self.xc.labels[i] + ')'))
				child.setIcon(0, helpers.layer_icon(self.xc[i]))
				child.setCheckState(0, 0)

				self.num_rows = self.num_rows + 1
				disableSubset = False
				temp = False

				for j in range(0, len(self.xc.subset_groups)):
					childtwo = QTreeWidgetItem(parent)
					childtwo.setData(0, 0, '{}'.format(self.xc.subset_groups[j].label))
					# child.setEditable(False)
					childtwo.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
					childtwo.setCheckState(0, 0)

					if (not disableSubset) and (not temp):
						try:
							 self.xc[i].compute_statistic('minimum', self.xc[i].subsets[j].components[k], subset_state=self.xc.subset_groups[j].subset_state)
							 #self.xc[i].compute_statistic('minimum', self.dc[i].subsets[j].components[k], subset_state=self.dc[i].subsets[j].subset_state)
							 temp = True
						except:
							#child.setData(0, Qt.CheckStateRole, QVariant())
							disableSubset = True
					if disableSubset:
						childtwo.setData(0, Qt.CheckStateRole, QVariant())
						childtwo.setForeground(0,QtGui.QBrush(Qt.gray))


					self.num_rows = self.num_rows + 1
