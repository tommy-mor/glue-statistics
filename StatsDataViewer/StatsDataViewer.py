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
from glue.core.message import DataMessage, DataCollectionMessage, SubsetMessage, SubsetCreateMessage, SubsetUpdateMessage, \
	LayerArtistUpdatedMessage, NumericalDataChangedMessage, DataUpdateMessage, DataAddComponentMessage, DataRemoveComponentMessage, DataCollectionDeleteMessage,\
	SubsetDeleteMessage, EditSubsetMessage
from PyQt5.QtGui import QStandardItemModel
from PyQt5 import QtGui
from PyQt5.QtWidgets import QAction
from glue.icons.qt import helpers
from qtpy import compat, QtWidgets





@viewer_tool
class convertNotation(Tool):
	#icon = '/StatsDataViewer/glue_scientific_notation.png'
	tool_id = 'notation_tool'
	action_text = 'Convert'
	tool_tip = 'Click icon to toggle Scientific noation or decimal'
	status_tip = 'Click to toggle notation'
	shortcut = 'N'

	def __init__(self,viewer):
		self.viewer = viewer

	def menu_actions(self):
		self.decimalPoints = QAction("Decimal Points")
		return [self.decimalPoints]

	def activate(self):
		#self.icon = '/Users/jk317/Glue/icons/glue_scientific_notation.png'
		#print("Convert button activate")
		self.viewer.pressedEventConvertNotation(not self.viewer.isSci)

	def close(self):
		pass

@viewer_tool
class ExportButton(Tool):
	#icon = '/StatsDataViewer/glue_export.png'
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

	#icon = '/StatsDataViewer/glue_home'
	tool_id = 'home_tool'
	action_text = 'Return to Home'
	tool_tip = 'Click to return to home'
	status_tip = 'Click to return to home'
	shortcut = 'H'

	def __init__(self, viewer):
		self.viewer = viewer

	def activate(self):
		self.viewer.nestedtree.collapseAll()

	def close(self):
		pass

@viewer_tool
class TreeButton(Tool):

	#icon = '/StatsDataViewer/glue_hierarchy.png'
	tool_id = 'move_tool'
	action_text = 'move'
	tool_tip = 'Drag to move'
	status_tip = 'Drag to move'
	shortcut = 'M'

	def __init__(self, viewer):
		self.viewer = viewer

	def activate(self):
		if self.viewer.component_mode:
			self.viewer.sortBySubsets()
		else:
			self.viewer.sortByComponents()

	def close(self):
		pass

@viewer_tool
class ExpandButton(Tool):

	#icon = '/StatsDataViewer/glue_expand.png'
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

	#icon = '/StatsDataViewer/glue_calculate.png'
	tool_id = 'calc_tool'
	action_text = 'Calculate'
	tool_tip = 'Click side icons to calculate'
	status_tip = 'Click to calculate'
	shortcut = 'C'

	def __init__(self, viewer):
		self.viewer = viewer

	def activate(self):
		#print("Calculate button activate")
		self.viewer.pressedEventCalculate()
		#print(self.viewer.layers[0].layer)

	def close(self):
		pass

@viewer_tool
class SortButton(CheckableTool):

	#icon = '/StatsDataViewer/glue_sort.png'
	tool_id = 'sort_tool'
	action_text = 'Sort'
	tool_tip = 'Click side icons to sort'
	status_tip = 'Choose a column to sort by. When you are done, deactivate sort mode.'
	shortcut = 'S'

	def __init__(self, viewer):
		super(CheckableTool, self).__init__(viewer)
		# self.viewer = viewer

	def activate(self):
		# ifSortingEnabled(), disable, otherwise, enable
		self.viewer.nestedtree.setSortingEnabled(True)

	def deactivate(self):
		self.viewer.nestedtree.setSortingEnabled(False)
		# pass

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

	LABEL = 'Statistics viewer'
	_state_cls = StatsViewerState
	_options_cls = StatsViewerStateWidget


	_toolbar_cls = BasicToolbar
	tools = ['home_tool', 'move_tool', 'calc_tool', 'sort_tool', 'notation_tool', 'export_tool'] #  'expand_tool'



	def __init__(self, *args, **kwargs):

		super(StatsDataViewer, self).__init__(*args, **kwargs)
		#HubListener.__init__(self)
		self.xc = self.session.data_collection# dc = DataCollection()


		#self.xc.hub.subscribe(self, DataMessage, handler=self.messageReceived)
		#self.xc.hub.subscribe(self, SubsetCreateMessage, handler=self.messageReceived)
		#self.xc.hub.subscribe(self, SubsetMessage, handler=self.messageReceived)
		#self.xc.hub.subscribe(self, DataAddComponentMessage, handler=self.messageReceived)
		#self.xc.hub.subscribe(self, DataCollectionMessage, handler=self.newDataAddedMessage)
		#self.xc.hub.subscribe(self, DataRemoveComponentMessage, handler=self.dataRemovedMessage)
		#self.xc.hub.subscribe(self, SubsetUpdateMessage, handler=self.messageReceived)
		#self.xc.hub.subscribe(self, LayerArtistUpdatedMessage, handler=self.messageReceived)
		#self.xc.hub.subscribe(self, NumericalDataChangedMessage, handler=self.messageReceived)

		self.no_update = True
		self.calculatedList = np.array(["Subset,Dataset,Component,Mean,Median,Minimum,Maximum,Sum"])

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
		self.nestedtree = QTreeWidget(self)
		self.nestedtree.setSelectionMode(QAbstractItemView.MultiSelection)
		self.nestedtree.setColumnCount(6)
		self.nestedtree.setColumnWidth(0, 300)
		self.nestedtree.header().setSortIndicator(1, 0)
		QTreeWidget.setHeaderLabels(self.nestedtree, self.headings)
		self.setCentralWidget(self.nestedtree)
		self.nestedtree.itemClicked.connect(self.check_status)



		# Set up dicts for row indices
		self.subset_dict = dict()
		self.component_dict = dict()
		self.selected_dict = dict()


		#sets the default view to subset view
		#self.nestedtree = self.subsetTree
		self.sortBySubsets()

		#keeps track of how much data and subsets are loaded in
		self.dc_count = 0
		self.subset_count = 0

		self.data_names = self.xc.labels
		self.subset_names = self.subsetNames()

		self.subset_set = set()

	def register_to_hub(self, hub):
		super(StatsDataViewer, self).register_to_hub(hub)

		hub.subscribe(self, DataCollectionMessage, handler=self.newDataAddedMessage)
		hub.subscribe(self, DataCollectionDeleteMessage, handler=self.dataDeleteMessage)
		hub.subscribe(self, SubsetCreateMessage, handler=self.subsetCreatedMessage)
		hub.subscribe(self, SubsetDeleteMessage, handler=self.subsetDeleteMessage)
		hub.subscribe(self, DataUpdateMessage, handler=self.dataUpdateMessage)
		hub.subscribe(self, SubsetUpdateMessage, handler=self.subsetUpdateMessage)
		#hub.subscribe(self, EditSubsetMessage, handler=self.editSubsetMessage)
		#hub.subscribe(self, LayerArtistUpdatedMessage, handler=self.layerArtistUpdatedMessage)
		#hub.subscribe(self, DataRemoveComponentMessage, handler=self.dataRemovedMessage)
		#hub.subscribe(self, DataUpdateMessage, handler=self.dataRemovedMessage)


	def check_status(self, item , col):

		#if the viewer is in subset mode
		if not self.component_mode:

			if item.checkState(0):
				#print("checked")
				#if the data branch is selected, check everything under data branch
				self.check_status_helper(2, item)

			else:
				#print("unchecked")
				# 0 means to uncheck NOTE: This is different then checkState. 0 for checkState means it is checked
				self.check_status_helper(0, item)

	def check_status_helper(self, state, dataset):

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
		new_names = []
		for x in self.xc.subset_groups:
			new_names.append(x.label)
		return np.array(new_names)

	def subsetUpdateMessage(self, message):
		#print("subsetupdate")
		#print(message)
		index1 = str(message).index("Subset: ") + len("Subset: ")
		index2 = str(message).index(" (data: ")
		new_name = str(message)[index1:index2]

		new_names = self.subsetNames()
		new_names = np.array(new_names)
		old_name = np.setdiff1d(self.subset_names, new_names)
		#print(self.subset_names)

		subset_branch = self.nestedtree.invisibleRootItem().child(1)
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


		self.subset_names = self.subsetNames()

	def dataUpdateMessage(self, message):
		#print(message)
		#first section of changing name
		index1 = str(message).index("Data Set: ") + len("Data Set: ")
		index2 = str(message).index("Number of dimensions: ") - 1
		new_name = str(message)[index1:index2]

		new_names = self.xc.labels
		old_name = np.setdiff1d(self.data_names, new_names)

		data_branch = self.nestedtree.invisibleRootItem().child(0)
		child_count = data_branch.childCount()
		if len(old_name) == 0:
			#the name has not changed, so changed color
			old_name = "name is the same"
			for i in range(child_count):
				data_branch.child(i).setIcon(0, helpers.layer_icon(self.xc[i]))
				component_count = data_branch.child(i).childCount()
				for x in range(component_count):
					data_branch.child(i).child(x).setIcon(0, helpers.layer_icon(self.xc[i]))
		else:
			#update the dataset name in the statsviewer
			old_name = old_name[0]
			for i in range(child_count):
				if data_branch.child(i).data(0,0) == old_name:
					data_branch.child(i).setData(0,0, new_name)

			#update the subsets that contain the old name, if any
			if len(self.xc.subset_groups) != 0:
				print(old_name)
				print(new_name)
				subset_branch = self.nestedtree.invisibleRootItem().child(1)
				child_count = subset_branch.childCount()
				for i in range(child_count):
					component_count = subset_branch.child(i).childCount()
					for x in range(component_count):
						#print(old_name)
						#print(subset_branch.child(i).child(x).data(0,0))
						if "(" + str(old_name) + ")" in str(subset_branch.child(i).child(x).data(0,0)):
							new_label = str(subset_branch.child(i).child(x).data(0,0)).replace(str(old_name),str(new_name))
							subset_branch.child(i).child(x).setData(0,0,new_label)

		self.data_names = self.xc.labels

	def editSubsetMessage(self, message):
		print("detected subset edit")
		#print(message)

	def newDataAddedMessage(self, message):
		print("detected new data added")
		self.dc_count += 1
		print(message)


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


	def subsetCreatedMessage(self, message):
		print("detected new subset creation")
		#print(message)

		index1 = str(message).index("Subset: ") + len("Subset: ")
		index2 = str(message).index(" (data: ")
		current_subset = str(message)[index1:index2]
		print(current_subset)




		if not current_subset in self.subset_set:
		#if not current_subset in self.subset_dict:

			j = self.subset_count
			grandparent = QTreeWidgetItem(self.subsetItem)
			grandparent.setData(0, 0, '{}'.format(self.xc.subset_groups[j].label))
			grandparent.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
			grandparent.setCheckState(0, 0)
			count = 0
			for i in range(0, len(self.xc)):
				count = i-1
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

			self.subset_set.add(current_subset)
			#self.subset_dict[current_subset].append(count)
			self.subset_count += 1

			#if self.subset_dict.get(current_subset) != self.dc_count:
			#	print("add the code")


	def dataDeleteMessage(self,message):
		print("detected data removal")
		print(message)
		self.deleteHelper('dataset')
		self.dc_count -= 1

	def subsetDeleteMessage(self, message):
		print("detected subset deletion")
		self.deleteHelper('subset')
		self.subset_count -= 1

	def deleteHelper(self, deletedType):
		print(deletedType)
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

		#data branch of tree
		data_branch = self.nestedtree.invisibleRootItem().child(temp)
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
				self.subset_set.remove(str(toBeRemoved))
			#print(self.subset_set)

	def initialize_toolbar(self):
		super(StatsDataViewer, self).initialize_toolbar()
		BasicToolbar.setContextMenuPolicy(self,Qt.PreventContextMenu)

	def myPressedEvent(self, currentQModelIndex):
		pass

	def expandAll(self, bool):

		item_List = self.past_itemMasterList

		for qtwitem in item_List:
			qtwitem.setExpanded(bool)

	def reconfigureTree(self):
		print("reconfiguring tree")

	def pressedEventCalculate(self):
		'''
		Every time the selection in the treeview changes:
		if it is newly selected, add it to the table
		if it is newly deselected, remove it from the table
		'''

		self.selected_indices = []

		#print(self.selected_indices)
		#print("000002")

		# create list of rows to calculate
		if not self.component_mode:
			data_branch = self.nestedtree.invisibleRootItem().child(0)
			for data_i in range (0, len(self.xc)):

				for comp_i in range (0, len(self.xc[data_i].components)):

					# if checked, add to selected list
					if data_branch.child(data_i).child(comp_i).checkState(0): #or self.nestedtree.invisibleRootItem().child(0).child(data_i).checkState(0) or self.nestedtree.invisibleRootItem().child(0).checkState(0):
						self.selected_indices.append(
							self.nestedtree.indexFromItem(data_branch.child(data_i).child(comp_i)))
					else:
						pass
			subset_branch = self.nestedtree.invisibleRootItem().child(1)
			for subset_i in range (0, len(self.xc.subset_groups)):
				print("subset: "+ str(subset_i))
				for data_i in range (0, len(self.xc)):
					print("the weird thing: "+ str(data_i))
					for comp_i in range (0, len(self.xc[data_i].components)):
						print("component: "+ str(comp_i))
						if subset_branch.child(subset_i).child(data_i).child(comp_i).checkState(0):# or self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).child(subset_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).checkState(0):
							#print("lalalal")
							self.selected_indices.append(
								self.nestedtree.indexFromItem(subset_branch.child(subset_i).child(data_i).child(comp_i)))

		else:
			for data_i in range(0,len(self.xc)):

				# subset_i and comp_i are switched by accident
				for subset_i in range(0, len(self.xc[data_i].components)):

					for comp_i in range(0, len(self.xc.subset_groups) + 1):

						if self.nestedtree.invisibleRootItem().child(data_i).child(subset_i).child(comp_i).checkState(0): # or self.nestedtree.invisibleRootItem().child(data_i).child(subset_i).checkState(0) or self.nestedtree.invisibleRootItem().child(data_i).checkState(0):
							self.selected_indices.append(
								self.nestedtree.indexFromItem(self.nestedtree.invisibleRootItem().child(data_i).child(subset_i).child(comp_i)))
						else :
							pass

		newly_selected = np.setdiff1d(self.selected_indices, self.past_selected)
		#print(self.selected_indices)
		#print("xaxaxaxa")
		#print(self.selected_indices[0])
		for index in range (0, len(newly_selected)):

			# Check which view mode the tree is in to get the correct indices
			if not self.component_mode:

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
			for col_index in range (0, len(new_data)):
				self.calculatedList = np.append(self.calculatedList, new_data[col_index])
				if (col_index > 2):
					#print(new_data[col_index])
					self.nestedtree.itemFromIndex(newly_selected[index]).setData(col_index-2, 0, new_data[col_index])

	def pressedEventExport(self):

		file_name, fltr = compat.getsavefilename(caption="Choose an output filename")
		try:
			df = pd.DataFrame(self.calculatedList)
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
		self.pressedEventCalculate()

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
		self.pressedEventCalculate()

		# uncheck everything
		for qtwitem in uncheck_list:
			qtwitem.setCheckState(0, 0)

		# recheck checked list items
		for qtwitem in checked_list:
			qtwitem.setCheckState(0, 2)

	def runDataStats (self, data_i, comp_i):
		'''
		Runs statistics for the component comp_i of data set data_i
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
		self.nestedtree.clearSelection()

		# Clear the tree
		self.nestedtree.clear()

		#Allow the user to select multiple rows at a time
		self.selection_model = QAbstractItemView.MultiSelection
		self.nestedtree.setSelectionMode(self.selection_model)


		self.nestedtree.setUniformRowHeights(True)

		self.generateSubsetView()
		# self.nestedtree.header.moveSection(1, 0)

		# Make the table update whenever the selection in the tree is changed
		selection_model = QItemSelectionModel(self.model_subsets)
		#self.nestedtree.setSelectionModel(selection_model)
		selection_model.selectionChanged.connect(self.myPressedEvent)

		return self.nestedtree

	def generateSubsetView(self):
		#self.component_mode = False
		self.model_subsets = QStandardItemModel()
		self.model_subsets.setHorizontalHeaderLabels([''])

		self.dataItem =  QTreeWidgetItem(self.nestedtree)
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



		self.subsetItem = QTreeWidgetItem(self.nestedtree)
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



		self.nestedtree.setUniformRowHeights(True)


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
		self.nestedtree.clearSelection()
		self.nestedtree.clear()


		self.selection_model = QAbstractItemView.MultiSelection
		self.nestedtree.setSelectionMode(self.selection_model)


		self.generateComponentView()

		self.nestedtree.setUniformRowHeights(True)

		return self.nestedtree

	def generateComponentView(self):
		self.component_mode = True

		for i in range(0,len(self.xc)):

			grandparent = QTreeWidgetItem(self.nestedtree)
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

				for j in range(0, len(self.xc.subset_groups)):
					childtwo = QTreeWidgetItem(parent)
					childtwo.setData(0, 0, '{}'.format(self.xc.subset_groups[j].label))
					# child.setEditable(False)
					childtwo.setIcon(0, helpers.layer_icon(self.xc.subset_groups[j]))
					childtwo.setCheckState(0, 0)


					self.num_rows = self.num_rows + 1
