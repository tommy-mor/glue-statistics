import os
import time
import numpy as np

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
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

from glue.viewers.image.qt import ImageViewer

from glue.utils.qt import load_ui

from decimal import getcontext, Decimal

import sys
from glue.core import DataCollection, Hub, HubListener, Data
from glue.core.link_helpers import LinkSame
from glue.core.message import DataMessage, DataCollectionMessage, SubsetMessage, SubsetUpdateMessage

import pandas as pd
from pandas import DataFrame

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from glue.icons.qt import helpers

from PyQt5 import QtCore, QtWidgets, QtGui



image_filename = '/Users/Dan/Downloads/w5/w5.fits'
catalog_filename = '/Users/Dan/Downloads/w5/w5_psc.vot'

#load 2 datasets from files
catalog = load_data(catalog_filename)
image = load_data(image_filename)

dc = DataCollection([catalog,image])

# link positional information
dc.add_link(LinkSame(catalog.id['RAJ2000'], image.id['Right Ascension']))
dc.add_link(LinkSame(catalog.id['DEJ2000'], image.id['Declination']))

#Create subset based on filament mask
ra_state = (image.id['Right Ascension'] > 44) & (image.id['Right Ascension'] < 46)
subset_group = dc.new_subset_group('Subset 1', ra_state)
subset_group.style.color = '#FF0000'

de_state = image.id['Declination'] > 60
subset_group1 = dc.new_subset_group('Subset 2', de_state)
subset_group1.style.color = '#00FF00'

j_state = catalog.id['Jmag'] > 14
subset_group2 = dc.new_subset_group('Jmag Selection', j_state)
subset_group2.style.color = '#00FF00'


@viewer_tool
class HomeButton(CheckableTool):

	icon = 'glue_home'
	tool_id = 'home_tool'
	action_text = 'Return to Home'
	tool_tip = 'Click to return to home'
	status_tip = 'Click to return to home'
	shortcut = 'H'

	def __init__(self, viewer):
		super(CheckableTool, self).__init__(viewer)

	def activate(self):
		pass

	def deactivate(self):
		pass

	def close(self):
		pass

@viewer_tool
class TreeButton(Tool):

	icon = '/Users/Dan/Documents/glue/icons/glue_hiearchy.png'
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

	icon = '/Users/Dan/Documents/glue/icons/glue_expand.png' 
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

	icon = '/Users/Dan/Documents/glue/icons/glue_calculate.png'
	tool_id = 'calc_tool'
	action_text = 'Calculate'
	tool_tip = 'Click side icons to calculate'
	status_tip = 'Click to calculate'
	shortcut = 'C'

	def __init__(self, viewer):
		self.viewer = viewer

	def activate(self):
		print("Calculate button activate")
		self.viewer.pressedEventFour()
		print(self.viewer.layers[0].layer)

	def close(self):
		pass

@viewer_tool
class SortButton(CheckableTool):

	icon = '/Users/Dan/Documents/glue/icons/glue_sort.png'
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

		# self.viewer.convertNotation()

	def deactivate(self):
		self.viewer.nestedtree.setSortingEnabled(False)
		# pass

	def close(self):
		pass

# class TreeSortButton(Tool):

#     icon = '/Users/Dan/Documents/glue/icons/glue_sort.png'
#     tool_id = 'sort_tool'
#     action_text = 'Sort'
#     tool_tip = 'Click side icons to sort'
#     status_tip = 'Click side icons to sort'
#     shortcut = 'S'

#     def __init__(self, viewer):
#         super(CheckableTool, self).__init__(viewer)

#     def activate(self):
#         # self.nestedtree.setSortingEnabled(True)
#         pass

#     def deactivate(self):
#         # ignore /////nestedtree.setColumnHidden(6, True)
#         pass

#     def close(self):
#         pass

class TutorialViewerState(ViewerState):

	expandAll = CallbackProperty(False, docstring='The button which expands or collapses all items')
	# sort_by = CallbackProperty(False, docstring='sets notation')
	decPlaces = CallbackProperty()

	numNotation = CallbackProperty(False, docstring='The button which changes number notation')
	# sort_type_button = SelectionCallbackProperty(docstring='The button which switches between tree sort types')
	# notation_bool = SelectionCallbackProperty(docstring='The attribute which determines if we are in Scientific or Decimal notation')
	# sig_num_att = SelectionCallbackProperty(docstring='The attribute which tells us the number of sig figs after the decimal')
	# x_att = SelectionCallbackProperty(docstring='The attribute to use on the x-axis')
	# y_att = SelectionCallbackProperty(docstring='The attribute to use on the y-axis')

	def __init__(self, *args, **kwargs):
		super(TutorialViewerState, self).__init__(*args, **kwargs)
		self.expandAll = False
		# self.component_mode = False
		self.numNotation = True
		# self.dec_places = 3

	def expand_all(self):
		self.expandAll = not self.expandAll
		# print(self.layers[0].layer)

		# print(self.layers)



	def change_notation(self):
		self.numNotation = not self.numNotation

	# def random_func(self):
	# 	pass

	# def sort_by(self):

	# 	print("sort button clicked")

	# def dec_places(self):
	# 	self.dec_places = self.dec_places + 1

	# # def 
	# def set_notation(self, bool):

	# 	print("set notation button clicked")




class TutorialViewerStateWidget(QWidget):

	def __init__(self, viewer_state=None, session=None):

		super(TutorialViewerStateWidget, self).__init__()

		self.ui = load_ui('viewer_state.ui', self,
						  directory=os.path.dirname(__file__))

		self.viewer_state = viewer_state 
		self._connections = autoconnect_callbacks_to_qt(self.viewer_state, self.ui)
		# self.ui.decimal_spinner.valueChanged.connect(self.state.decPlaces)
		# self.ui.pushButton.click.connect(self.viewer.expandAll(True))
		# self.ui.button_expand_all.click.connect(self.expand_all())
	# 	self.ui.button_change_notation.click.connect(self.changeText())


	# def changeText(self):
	# 	# print(self.ui.button_change_notation.setText
	# 	print("works")
	# def display_calc(self):
	#     pass




class TutorialDataViewer(DataViewer):

	LABEL = 'Statistics viewer'
	_state_cls = TutorialViewerState
	_options_cls = TutorialViewerStateWidget
	# _layer_style_widget_cls = TutorialLayerStateWidget
	# _data_artist_cls = TutorialLayerArtist
	# _subset_artist_cls = TutorialLayerArtist
	
	_toolbar_cls = BasicToolbar
	tools = ['home_tool', 'move_tool', 'calc_tool', 'sort_tool'] #  'expand_tool'


	#dc = dc



	def __init__(self, *args, **kwargs):
		super(TutorialDataViewer, self).__init__(*args, **kwargs)
		
		# dc = DataCollection()
		# self.dc = dc
		self.no_update = True

		self.headings = ('Name', 'Mean', 'Median', 'Minimum', 'Maximum', 'Sum')
		#dc = dc

		# Set up dicts for row indices
		self.subset_dict = dict()
		self.component_dict = dict()
		
		self.selected_dict = dict()
		self.selected_indices = []
		

		# Set up tree widget item 
		self.nestedtree = QTreeWidget(self)
		self.nestedtree.setSelectionMode(QAbstractItemView.NoSelection)
		
		#self.nestedtree
		#self.nestedtree.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

		self.nestedtree.setColumnCount(7)
		# self.nestedtree.setColumnHidden(6, True)
		self.nestedtree.setColumnWidth(0, 175)
		self.nestedtree.header().setSortIndicator(1, 0)
		
		# items = []
		# for i in range(9):
		#     items.append(QTreeWidgetItem(self.nestedtree)) #self.headings[i]
			#print(items[i])
			#items[i].setText(0, self.headings[i])
		#for i in range(9):
		#   
		# items[0].setText(0, 'Subset')       
		# items[1].setText(0, 'Dataset')
		# items[2].setText(0, ' ' + str(self.nestedtree.currentColumn()))

		self.isSci = True
		self.num_sigs = 3

		# Set up past selected items
		self.past_selected = []

		#self.headings = 
		QTreeWidget.setHeaderLabels(self.nestedtree, self.headings)
		self.axes = plt.subplot(1, 1, 1)
		self.setCentralWidget(self.nestedtree)
		#w5 = QTreeWidgetItem(items[0], "w5")
		#items[0].addChild
			##self.sort_by_subsets(self, dc.invisibleRootItem())
		
		# # Save the subset names
		# self.sub_names = []
		# for i in range(len(dc.subset_groups)):
		#     self.sub_names.append(dc.subset_groups[i].label)

		# # Save the dataset names
		# self.data_names = dc.labels

		# # Save the component names 
		# self.all_comp_names = []
		# component_names = []
		# for i in range(0, len(dc)):
		#     for j in range(0, len(dc[i].components)):
		#         component_names.append(dc[i].components[j].label)
		#     self.all_comp_names.append(component_names)
		#     component_names = []

		# # Set component_mode to false, default is subset mode
		self.component_mode = False

		# # These will only be true when the treeview has to switch between views and a
		# # Change has been made in the other
		self.updateSubsetSort = False
		self.updateComponentSort = False

		# Sort by subsets as a default
		self.sortBySubsets()
		# self.sortByComponents()
		print("ha")
		# self.fakeItem = QTreeWidgetItem(self.nestedtree)

		# self.fakeButton = QPushButton(self.nestedtree)

		# self.fakeItem.addWidget(QPushButton("xxxTESTxyx"))

		# Set up dict for caching
		self.cache_stash = dict()

		# self.myPressedEvent()

		# self.runDataStats(1, 2)

		# self.pressedEventTwo()
		self.nestedtree.clearSelection()

		# self.nestedtree.invisibleRootItem().child(0).child(0).sortChildren(1, 0)
		# # Allow the widget to listen for messages
		# dc.hub.subscribe(self, SubsetUpdateMessage, handler=self.receive_message)
		# dc.hub.subscribe(self, DataMessage, handler=self.messageReceived)
		# dc.hub.subscribe(self, SubsetMessage, handler=self.messageReceived)  
		# dc.hub.subscribe(self, DataCollectionMessage, handler=self.messageReceived)
		# dc.hub.subscribe(self, LayerArtistUpdatedMessage, handler=self.messageReceived)
		# dc.hub.subscribe(self, NumericalDataChangedMessage, handler=self.messageReceived)

		self.state.add_callback('expandAll', self.expandAll)
		# self.state.add_callback('sort_by', self.convertNotation)
		self.state.add_callback('decPlaces', self.decPlaces)
		self.state.add_callback('numNotation', self.convertNotation)

		# self.add_data()
		print(self.state.layers) # [0].layer
		# print(self._options_cls.layers)
		# print(self.state.layers[0])
		print(self.layers)
		# print(self.viewer.layers)
		# print(self._state_cls.layers[0].layer)

		self.data__ = self.dataList()
		print(self.data__)


		#for i in range(0, 6):
		#    self.nestedtree.resizeColumnToContents(i)

		#self.nestedtree.itemClicked    
		#https://stackoverflow.com/questions/16712420/qt-event-listener-for-tree-widget-item-click

		#self.nestedtree.setStyleSheet("QTreeWidget::item { border-bottom: 1px solid black;}")
	def myPressedEvent(self, currentQModelIndex):
		pass

	# def add_data(self, data):
	# 	print("data")
	# 	# if self.component_mode:
	# 	# 	self.sortByComponents()
	# 	# else:
	# 	# 	self.sortBySubsets()
	# 	self.dc.append(data)
	# 	return True

	def expandAll(self, bool):

		item_List = self.itemMasterList()

		for qtwitem in item_List:
			qtwitem.setExpanded(bool)

	def pressedEventTwo(self):
		''' 
		Every time the selection in the treeview changes:
		if it is newly selected, add it to the table
		if it is newly deselected, remove it from the table
		'''

		# Get the indexes of all the selected components
		self.selected_indices = self.nestedtree.selectionModel().selectedRows()

		print(self.selected_indices)
		print("000001")

		newly_selected = np.setdiff1d(self.selected_indices, self.past_selected)

		print("xaxaxaxa")
			
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

			print(new_data) 
			print("xoxoxo")   
			print(newly_selected[index].row())
			print("newly selected item ^")
			print(self.nestedtree.itemFromIndex(newly_selected[index]))
			print(new_data[0])
			print(new_data[1])
			print(new_data[2])
			# self.nestedtree.itemFromIndex(newly_selected[0]).setData(0, 0, new_data[0][0])
			for col_index in range (0, len(new_data)):
				if (col_index > 0):
					print("xxxxxx")
					print(new_data[col_index])
					self.nestedtree.itemFromIndex(newly_selected[index]).setData(col_index, 0, new_data[col_index])  

			# self.nestedtree.itemFromIndex(newly_selected[index]).setData(2, 0, 100)   
			
		newly_dropped = np.setdiff1d(self.past_selected, self.selected_indices)
			
		for index in range (0, len(newly_dropped)):
				
			# Check which view mode the tree is in to get the correct indices
			if not self.component_mode:
				data_i = newly_dropped[index].parent().row()
				comp_i = newly_dropped[index].row()
				subset_i = newly_dropped[index].parent().parent().row()
			
			else:
				data_i = newly_dropped[index].parent().parent().row()
				comp_i = newly_dropped[index].parent().row()
				subset_i = newly_dropped[index].row() - 1
			
			is_subset = newly_dropped[index].parent().parent().parent().row() == 1 or (self.switch_mode.text() == 'Sort tree by subsets' and subset_i != -1)

			if is_subset:
				try:
					# Get the indices that match the component, dataset, and subset requirements
					idx_c = np.where(self.data_frame['Component'] == dc[data_i].components[comp_i].label)
					idx_d = np.where(self.data_frame['Dataset'] == dc[data_i].label)
					idx_s = np.where(self.data_frame['Subset'] == dc[data_i].subsets[subset_i].label)
					idx1 = np.intersect1d(idx_c, idx_d)
					idx2 = np.intersect1d(idx1, idx_s)

					self.data_frame = self.data_frame.drop(idx2)
				except:
					pass

			else:
				try:
				# Find the index in the table of the unchecked element, if it's in the table

					# Find the matching component and dataset indices and intersect them to get the unique index
					idx_c = np.where(self.data_frame['Component'] == dc[data_i].components[comp_i].label)
					idx_d = np.where(self.data_frame['Dataset'] == dc[data_i].label)
					idx_s = np.where(self.data_frame['Subset'] == '--')
					idx1 = np.intersect1d(idx_c, idx_d)
					idx2 = np.intersect1d(idx1, idx_s)

					# self.data_frame = self.data_frame.drop(idx2)
				except:
					pass
		
		# Update the past selected indices
		self.past_selected = self.selected_indices
		
		# model = pandasModel(self.data_frame, dc)
		
		# self.table.setModel(model)
	   
		# self.table.setSortingEnabled(True)
		# self.table.setShowGrid(False)  

	def pressedEventFour(self):
		''' 
		Every time the selection in the treeview changes:
		if it is newly selected, add it to the table
		if it is newly deselected, remove it from the table
		'''

		# Get the indexes of all the selected components
		self.selected_indices = [] #self.nestedtree.selectionModel().selectedRows()

		print(self.selected_indices)
		print("000002")

		# create list of rows to calculate
		if not self.component_mode:
		
			for data_i in range (0, len(dc)):

				for comp_i in range (0, len(dc[data_i].components)):

					# if checked, add to selected list
					if self.nestedtree.invisibleRootItem().child(0).child(data_i).child(comp_i).checkState(0) or self.nestedtree.invisibleRootItem().child(0).child(data_i).checkState(0) or self.nestedtree.invisibleRootItem().child(0).checkState(0):
						self.selected_indices.append(
							self.nestedtree.indexFromItem(self.nestedtree.invisibleRootItem().child(0).child(data_i).child(comp_i)))
					else:
						pass

			for subset_i in range (0, len(dc.subset_groups)):

				for data_i in range (0, len(dc)):

					for comp_i in range (0, len(dc[data_i].components)):
						# print("xoxoxo")
						# print (self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).child(comp_i))
						if self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).child(comp_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).child(subset_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).checkState(0):
							print("lalalal")
							self.selected_indices.append(
								self.nestedtree.indexFromItem(self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).child(comp_i)))
						
		else:
			for data_i in range(0,len(dc)):

				# subset_i and comp_i are switched by accident
				for subset_i in range(0, len(dc[data_i].components)):

					for comp_i in range(0, len(dc.subset_groups) + 1):

						if self.nestedtree.invisibleRootItem().child(data_i).child(subset_i).child(comp_i).checkState(0) or self.nestedtree.invisibleRootItem().child(data_i).child(subset_i).checkState(0) or self.nestedtree.invisibleRootItem().child(data_i).checkState(0):
							self.selected_indices.append(
								self.nestedtree.indexFromItem(self.nestedtree.invisibleRootItem().child(data_i).child(subset_i).child(comp_i)))
						else :
							pass

		newly_selected = np.setdiff1d(self.selected_indices, self.past_selected)
		print(self.selected_indices)
		print("xaxaxaxa")
			
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

			print(new_data) 
			print("xoxoxo")   
			print(newly_selected[index].row())
			print("newly selected item ^")
			print(self.nestedtree.itemFromIndex(newly_selected[index]))
			print(new_data[0])
			print(new_data[1])
			print(new_data[2])
			# self.nestedtree.itemFromIndex(newly_selected[0]).setData(0, 0, new_data[0][0])
			for col_index in range (0, len(new_data)):
				if (col_index > 0):
					print("xxxxxx")
					print(new_data[col_index])
					self.nestedtree.itemFromIndex(newly_selected[index]).setData(col_index, 0, new_data[col_index])  

			# self.nestedtree.itemFromIndex(newly_selected[index]).setData(2, 0, 100)   
		# newly_dropped = np.setdiff1d(self.past_selected, self.selected_indices)
		# for index in range (0, len(newly_dropped)):
				
		# 	# Check which view mode the tree is in to get the correct indices
		# 	if not self.component_mode:
		# 		data_i = newly_dropped[index].parent().row()
		# 		comp_i = newly_dropped[index].row()
		# 		subset_i = newly_dropped[index].parent().parent().row()
			
		# 	else:
		# 		data_i = newly_dropped[index].parent().parent().row()
		# 		comp_i = newly_dropped[index].parent().row()
		# 		subset_i = newly_dropped[index].row() - 1
			
		# 	is_subset = newly_dropped[index].parent().parent().parent().row() == 1 or (self.component_mode and subset_i != -1)

		# 	if is_subset:
		# 		try:
		# 			# Get the indices that match the component, dataset, and subset requirements
		# 			idx_c = np.where(self.data_frame['Component'] == dc[data_i].components[comp_i].label)
		# 			idx_d = np.where(self.data_frame['Dataset'] == dc[data_i].label)
		# 			idx_s = np.where(self.data_frame['Subset'] == dc[data_i].subsets[subset_i].label)
		# 			idx1 = np.intersect1d(idx_c, idx_d)
		# 			idx2 = np.intersect1d(idx1, idx_s)

		# 			self.data_frame = self.data_frame.drop(idx2)
		# 		except:
		# 			pass

		# 	else:
		# 		try:
		# 		# Find the index in the table of the unchecked element, if it's in the table

		# 			# Find the matching component and dataset indices and intersect them to get the unique index
		# 			idx_c = np.where(self.data_frame['Component'] == dc[data_i].components[comp_i].label)
		# 			idx_d = np.where(self.data_frame['Dataset'] == dc[data_i].label)
		# 			idx_s = np.where(self.data_frame['Subset'] == '--')
		# 			idx1 = np.intersect1d(idx_c, idx_d)
		# 			idx2 = np.intersect1d(idx1, idx_s)

		# 			# self.data_frame = self.data_frame.drop(idx2)
		# 		except:
		# 			pass
		
		# # Update the past selected indices
		# self.past_selected = self.selected_indices
		
		# model = pandasModel(self.data_frame, dc)
		
		# self.table.setModel(model)
	   
		# self.table.setSortingEnabled(True)
		# self.table.setShowGrid(False) 

	def itemMasterList(self):

		item_Master_List = []

		# create list of rows to calculate
		if not self.component_mode:

			item_Master_List.append(self.nestedtree.invisibleRootItem().child(0))

			for data_i in range (0, len(dc)):

				item_Master_List.append(self.nestedtree.invisibleRootItem().child(0).child(data_i))

				for comp_i in range (0, len(dc[data_i].components)):

					item_Master_List.append(self.nestedtree.invisibleRootItem().child(0).child(data_i).child(comp_i))

			item_Master_List.append(self.nestedtree.invisibleRootItem().child(1))

			for subset_i in range (0, len(dc.subset_groups)):

				item_Master_List.append(self.nestedtree.invisibleRootItem().child(1).child(subset_i))

				for data_i in range (0, len(dc)):

					item_Master_List.append(self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i))

					for comp_i in range (0, len(dc[data_i].components)):

						item_Master_List.append(self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).child(comp_i))

						
		else:

			for data_i in range(0, len(dc)):

				item_Master_List.append(self.nestedtree.invisibleRootItem().child(data_i))

				for comp_i in range(0, len(dc[data_i].components)):

					item_Master_List.append(self.nestedtree.invisibleRootItem().child(data_i).child(comp_i))

					for subset_i in range(0, len(dc.subset_groups) + 1):

						item_Master_List.append(self.nestedtree.invisibleRootItem().child(data_i).child(comp_i).child(subset_i))


		return item_Master_List


	def convertNotation(self, bool):
		'''
		Converts from scientific to decimal and vice versa

		'''
		item_List = self.itemMasterList()

		# list of current checked items so that we can re'check' them later
		checked_list = []

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

		print(checked_list)

		self.isSci = bool
		print("isSci changed")

		# self.expandAll(True)
		# print("expanded")

		# recalculate with new notation, 
		# data is cached already so it should be quick
		self.pressedEventFour()

		# uncheck everything
		for qtwitem in item_List:
			qtwitem.setCheckState(0, 0)

		# recheck checked list items
		for qtwitem in checked_list:
			qtwitem.setCheckState(0, 2)

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

		print(checked_list)

		self.num_sigs = intDecimal
		print("decimal changed")

		# self.expandAll(True)
		# print("expanded")

		# recalculate with new notation, 
		# data is cached already so it should be quick
		self.pressedEventFour()

		# uncheck everything
		for qtwitem in uncheck_list:
			qtwitem.setCheckState(0, 0)

		# recheck checked list items
		for qtwitem in checked_list:
			qtwitem.setCheckState(0, 2)

	def selectAll(self, bool_):
		'''
		select OR deselect all items in the tree
		based on given bool
		'''
		item_List = self.itemMasterList()

		for qtwitem in item_List:
			qtwitem.setCheckState(0, bool_)


	def runDataStats (self, data_i, comp_i):
		'''
		Runs statistics for the component comp_i of data set data_i
		'''

		subset_label = "--"
		data_label = dc[data_i].label   
		comp_label = dc[data_i].components[comp_i].label # add to the name array to build the table
		
		print("hihihi")
		print(data_label)
		print(comp_label)
		# Build the cache key
		cache_key = subset_label + data_label + comp_label
		
		print(cache_key)
		# See if the values have already been cached
		if True: # self.noupdate
			try:
				column_data = self.cache_stash[cache_key]
			except:
				column_data = self.newDataStats(data_i, comp_i)
		else:
			column_data = self.newDataStats(data_i, comp_i)    
		print(column_data)
		# Save the accurate data in self.data_accurate
		# column_df = pd.DataFrame(column_data, columns=self.headings)
		# self.data_accurate = self.data_accurate.append(column_df, ignore_index=True)        

		if self.isSci:
			# Format in scientific notation
			string = "%." + str(self.num_sigs) + 'E'
		else:
			# Format in standard notation
			string = "%." + str(self.num_sigs) + 'F'  

		print("xxyyzz")
		print(string)           

		mean_val = string % column_data[1]
		print(mean_val)
		print("mean_val ^^")
		median_val = string % column_data[2]
		min_val = string % column_data[3]
		max_val = string % column_data[4]
		sum_val = string % column_data[5]


		# DAN - I'm choosing to get rid of the df (DataFrame) since we no longer have two tables, only one
		# I'm instead making this retrn the column_data and putting it directly into the table.

		# Create the column data array and append it to the data frame
		column_data = (cache_key, mean_val, median_val, min_val, max_val, sum_val)
		# column_df = pd.DataFrame(column_data, columns=self.headings)
		# # self.data_frame = self.data_frame.append(column_df, ignore_index=True)
		return column_data

	
	def newDataStats(self, data_i, comp_i):
		print("newDataStats triggered")
		# Generates new data for a dataset that has to be calculated

		subset_label = "--"
		data_label = dc[data_i].label   
		comp_label = dc[data_i].components[comp_i].label # add to the name array to build the table
		
		# Build the cache key
		cache_key = subset_label + data_label + comp_label

		# Find the stat values
		# Save the data in the cache 
		mean_val = dc[data_i].compute_statistic('mean', dc[data_i].components[comp_i])
		median_val = dc[data_i].compute_statistic('median', dc[data_i].components[comp_i])     
		min_val = dc[data_i].compute_statistic('minimum', dc[data_i].components[comp_i])     
		max_val = dc[data_i].compute_statistic('maximum', dc[data_i].components[comp_i])    
		sum_val = dc[data_i].compute_statistic('sum', dc[data_i].components[comp_i])

		column_data = (cache_key, mean_val, median_val, min_val, max_val, sum_val)
			
		self.cache_stash[cache_key] = column_data

		return column_data

	def runSubsetStats (self, subset_i, data_i, comp_i):
		'''
		Runs statistics for the subset subset_i with respect to the component comp_i of data set data_i
		'''

		subset_label = dc[data_i].subsets[subset_i].label
		data_label = dc[data_i].label   
		comp_label = dc[data_i].components[comp_i].label # add to the name array to build the table
		
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
		
		# Save the data in self.data_accurate
		# column_df = pd.DataFrame(column_data, columns=self.headings)
		# self.data_accurate = self.data_accurate.append(column_df, ignore_index=True)        
		
		if self.isSci:
			# Format in scientific notation
			string = "%." + str(self.num_sigs) + 'E'
		else:
			# Format in standard notation
			string = "%." + str(self.num_sigs) + 'F'            
			
		mean_val = string % column_data[1]
		print(mean_val)
		print("mean_val ^")
		median_val = string % column_data[2]
		min_val = string % column_data[3]
		max_val = string % column_data[4]
		sum_val = string % column_data[5]
		
		# Create the column data array and append it to the data frame
		column_data = (cache_key, mean_val, median_val, min_val, max_val, sum_val)
		# column_df = pd.DataFrame(column_data, columns=self.headings)
		# self.data_frame = self.data_frame.append(column_df, ignore_index=True)  
		return column_data

	def newSubsetStats(self, subset_i, data_i, comp_i):
		# Generates new data for a subset that needs to be calculated
		subset_label = dc[data_i].subsets[subset_i].label
		data_label = dc[data_i].label   
		comp_label = dc[data_i].components[comp_i].label # add to the name array to build the table

		# Build the cache key
		cache_key = subset_label + data_label + comp_label

		mean_val = dc[data_i].compute_statistic('mean', dc[data_i].subsets[subset_i].components[comp_i], subset_state=dc[data_i].subsets[subset_i].subset_state)
		median_val = dc[data_i].compute_statistic('median', dc[data_i].subsets[subset_i].components[comp_i], subset_state=dc.subset_groups[subset_i].subset_state)       
		min_val = dc[data_i].compute_statistic('minimum', dc[data_i].subsets[subset_i].components[comp_i], subset_state=dc.subset_groups[subset_i].subset_state)       
		max_val = dc[data_i].compute_statistic('maximum', dc[data_i].subsets[subset_i].components[comp_i], subset_state=dc.subset_groups[subset_i].subset_state)      
		sum_val = dc[data_i].compute_statistic('sum', dc[data_i].subsets[subset_i].components[comp_i], subset_state=dc.subset_groups[subset_i].subset_state) 

		column_data = (cache_key, mean_val, median_val, min_val, max_val, sum_val)

		self.cache_stash[cache_key] = column_data  

		return column_data


	def mousePressEvent(self, event):
		pass

	def dataList(self):
		result = []
		print(self._state_cls.layers)
		# for dataOrSubset in self._state_cls.layers:
		# 	if dataOrSubset is Data:
		# 		result.append(dataOrSubset)

		return result


	def subsetList(self):
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
		
		# # Set Expand/collapse button to "expand all"
		# self.expand_data.setText("Expand all data and subsets")       
		
		#Allow the user to select multiple rows at a time 
		self.selection_model = QAbstractItemView.MultiSelection
		self.nestedtree.setSelectionMode(self.selection_model)
		
		
		self.nestedtree.setUniformRowHeights(True)
		
		self.generateSubsetView()
		# self.nestedtree.header.moveSection(1, 0)

		# Make the table update whenever the selection in the tree is changed
		selection_model = QItemSelectionModel(self.model_subsets)
		self.nestedtree.setSelectionModel(selection_model)
		selection_model.selectionChanged.connect(self.myPressedEvent)

		

		# # Clear the table 
		# self.data_frame = pd.DataFrame(columns=self.headings)
		# model = pandasModel(self.data_frame, dc)
		# self.table.setModel(model)
		# self.table.setSortingEnabled(True)
		# self.table.setShowGrid(False)
		
		# # Select rows that should be selected
		
		# sel_mod = self.nestedtree.selectionModel()
		
		# for i in range(0, len(selected)):
		#     key = list(selected.keys())[i]
		#     index = self.subset_dict[key]
		#     self.nestedtree.setCurrentIndex(index)
	
		# self.nestedtree.setSelectionModel(sel_mod)
		
		# # Update the past_selected and selected_indices
		# self.past_selected = self.nestedtree.selectionModel().selectedRows()
		# self.selected_indices = self.nestedtree.selectionModel().selectedRows()

	def generateSubsetView(self):
		self.component_mode = False
		self.model_subsets = QStandardItemModel()
		self.model_subsets.setHorizontalHeaderLabels([''])

		#self.nestedtree.setModel(self.model_subsets)
		# self.nestedtree.setUniformRowHeights(True)


		# populate the tree
		# Make all the datasets be parents, and make it so they are not selectable
					# parent_data = QStandardItem('{}'.format('Data')) # QStandardItem
		dataItem =  QTreeWidgetItem(self.nestedtree)
		dataItem.setData(0, 0, '{}'.format('Data'))
		# dataItem.setExpanded(True)
		dataItem.setCheckState(0, 0)
		# dataItem.setEditable(False)
		# dataItem.setSelectable(False)

		for i in range(0, len(dc)):

			parentItem = QTreeWidgetItem(dataItem)
			parentItem.setCheckState(0, 0)
			parentItem.setData(0, 0, '{}'.format(dc.labels[i]))
			parentItem.setIcon(0, helpers.layer_icon(dc[i]))
			# parentItem.setExpanded(True)
			# parentItem.setEditable(False)
			# parentItem.setSelectable(False)

			# Make all the data components be children, nested under their parent
			for j in range(0,len(dc[i].components)):

				childItem = QTreeWidgetItem(parentItem)
				childItem.setCheckState(0, 0)
				childItem.setData(0, 0, '{}'.format(str(dc[i].components[j])))
				childItem.setIcon(0, helpers.layer_icon(dc[i]))
				# childItem.setEditable(False)
				# childItem.setSelected(True)


				# Add to the subset_dict
				key = dc[i].label + dc[i].components[j].label + "All data-" + dc[i].label
				#self.subset_dict[key] = child.index()
				
				#parent.appendRow(child)

				self.num_rows = self.num_rows + 1

			#parent_data.appendRow(parent)
			# moves to below line, parent.setSelectable(False)
			

		# # Add the parents with their children to the QStandardItemModel
		# self.model_subsets.appendRow(parent_data)

		# parent_subset = QStandardItem('{}'.format('Subsets')) 
		# parent_subset.setEditable(False)
		# parent_subset.setSelectable(False)

		subsetItem = QTreeWidgetItem(self.nestedtree)
		subsetItem.setData(0, 0, '{}'.format('Subsets'))
		subsetItem.setCheckState(0, 0)

		# subsetItem.setCheckState(0, 0)

		# Set up the subsets as Subsets > choose subset > choose data set > choose component

		for j in range(0, len(dc.subset_groups)):

			grandparent = QTreeWidgetItem(subsetItem)
			grandparent.setData(0, 0, '{}'.format(dc.subset_groups[j].label))
			grandparent.setIcon(0, helpers.layer_icon(dc.subset_groups[j]))
			grandparent.setCheckState(0, 0)
			# grandparent.setCheckState(0, 0)
			# grandparent.setEditable(False)
			# grandparent.setSelectable(False)

			for i in range(0, len(dc)):

				parent = QTreeWidgetItem(grandparent)
				parent.setData(0, 0, '{}'.format(dc.subset_groups[j].label) + ' (' + '{}'.format(dc[i].label) + ')')
				# parent.setCheckState(0, 0)
				# Set up the circles
				parent.setIcon(0, helpers.layer_icon(dc.subset_groups[j]))
				parent.setCheckState(0, 0)
				# parent.setEditable(False)
				# parent.setSelectable(False)

				# try:
				#     dc[i].compute_statistic('mean', dc[i].subsets[j].components[0], subset_state=dc[i].subsets[j].subset_state)

				# except:
				#     parent.setForeground(QtGui.QBrush(Qt.gray))


				for k in range(0, len(dc[i].components)):

					child = QTreeWidgetItem(parent)
					child.setData(0, 0, '{}'.format(str(dc[i].components[k])))
					# child.setEditable(False)
					child.setIcon(0, helpers.layer_icon(dc.subset_groups[j]))
					child.setCheckState(0, 0)
					# child.setCheckState(0, 0)
					# child.setSelected(True)
					# # Update the dict to keep track of row indices
					# key = dc[i].label + dc[i].components[k].label + dc[i].subsets[j].label
					# self.subset_dict[key] = child.index()
						
					# parent.appendRow(child)
					self.num_rows = self.num_rows + 1

					# # Make gray and unselectable components that aren't defined for a subset
					# try:
					#     dc[i].compute_statistic('mean', dc[i].subsets[j].components[k], subset_state=dc[i].subsets[j].subset_state)

					# except:
					#     child.setEditable(False)
					#     child.setSelectable(False)
					#     child.setForeground(QtGui.QBrush(Qt.gray))

		#         grandparent.appendRow(parent) 
		#     parent_subset.appendRow(grandparent)
		# self.model_subsets.appendRow(parent_subset)
		
		# Fill out the dict now that the indices are connected to the QStandardItemModel
			
		# Full datasets
		# for i in range(0, parent_data.rowCount()):
		#     for j in range(0, parent_data.child(i).rowCount()):
		#         key = "All data (" + parent_data.child(i).text() + ")"+ parent_data.child(i).child(j).text()
		#         self.subset_dict[key] = parent_data.child(i).child(j).index()
			
		# # Subsets
		# for i in range(0, parent_subset.rowCount()):
		#     for j in range(0, parent_subset.child(i).rowCount()):
		#         for k in range(0, parent_subset.child(i).child(j).rowCount()):
		#             key = parent_subset.child(i).child(j).text() + parent_subset.child(i).child(j).child(k).text()
		#             self.subset_dict[key] = parent_subset.child(i).child(j).child(k).index()

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
		
		# # Save the selected rows from the subset view if applicable
		# try:
		#     selected = dict()

		#     for i in range(0, len(self.selected_indices)):
		#         item = self.model_subsets.itemFromIndex(self.selected_indices[i])
		#         if item.parent().parent().text() == "Data":
		#             key =  "All data (" + item.parent().text() + ")" + item.text()
		#             selected[key] = item.index()
		#         else:
		#             key = item.parent().text() + item.text()
		#             selected[key] = item.index()
		# except:
		#     pass
		
		# Clear the selection
		self.nestedtree.clearSelection()
		self.nestedtree.clear()
		
		# Set Expand/collapse button to "expand all"
		# self.expand_data.setText("Expand all data and subsets")
		
		self.selection_model = QAbstractItemView.MultiSelection
		self.nestedtree.setSelectionMode(self.selection_model)
		
		# See if the model already exists and doesn't need to be updated
		
		# if self.no_update and not self.updateComponentSort:
		#     try:
		#         self.nestedtree.setModel(self.model_components)
		#     except:
		#         self.generateComponentView()
		# else:
		#     self.generateComponentView()

		self.generateComponentView()

		self.nestedtree.setUniformRowHeights(True)
		
	#     # Make the table update whenever the tree selection is changed
	#     selection_model = QItemSelectionModel(self.model_components)
	#     self.treeview.setSelectionModel(selection_model)
	#     selection_model.selectionChanged.connect(self.myPressedEvent)
 
	#     # Clear the table 
	#     self.data_frame = pd.DataFrame(columns=self.headings)
	#     model = pandasModel(self.data_frame, dc)
	#     self.table.setModel(model)
	#     self.table.setSortingEnabled(True)
	#     self.table.setShowGrid(False)

		# Select the rows that should be selected

	#     sel_mod = self.treeview.selectionModel()
	
	#     for i in range(0, len(selected)):
	#         key = list(selected.keys())[i]
	#         index = self.component_dict[key]
	#         self.treeview.setCurrentIndex(index)
	
	#     self.treeview.setSelectionModel(sel_mod)
		
	#     # Update the past_selected and selected_indices
	#     self.past_selected = self.treeview.selectionModel().selectedRows() 
	#     self.selected_indices = self.treeview.selectionModel().selectedRows()
		
	def generateComponentView(self):
		self.component_mode = True
	#     self.model_components = QStandardItemModel()    
	#     self.model_components.setHorizontalHeaderLabels([''])

	#     self.treeview.setModel(self.model_components)
	#     self.treeview.setUniformRowHeights(True)
	
		# Populate the tree
		# Make all the datasets be parents, and make it so they are not selectable
		
		for i in range(0,len(dc)):
	#         grandparent = QStandardItem('{}'.format(dc.labels[i]))
			grandparent = QTreeWidgetItem(self.nestedtree)
			grandparent.setData(0, 0, '{}'.format(dc.labels[i]))
			grandparent.setIcon(0, helpers.layer_icon(dc[i]))
			grandparent.setCheckState(0, 0)
	#         grandparent.setEditable(False)
	#         grandparent.setSelectable(False)
			
			# Make all the data components be children, nested under their parent
			for k in range(0,len(dc[i].components)):
				parent = QTreeWidgetItem(grandparent)
				parent.setData(0, 0, '{}'.format(str(dc[i].components[k])))
				parent.setCheckState(0, 0)
				# parent.setEditable(False)
				# parent.setSelectable(False)
				
				child = QTreeWidgetItem(parent)
				child.setData(0, 0, '{}'.format('All data (' + dc.labels[i] + ')'))
				child.setIcon(0, helpers.layer_icon(dc[i]))
				child.setCheckState(0, 0)
	#             child.setEditable(False)
	#             child.setIcon(helpers.layer_icon(dc[i]))
					
	#             parent.appendRow(child)
				self.num_rows = self.num_rows + 1
				
				for j in range(0, len(dc.subset_groups)):
					childtwo = QTreeWidgetItem(parent)
					childtwo.setData(0, 0, '{}'.format(dc.subset_groups[j].label))
					# child.setEditable(False)
					childtwo.setIcon(0, helpers.layer_icon(dc.subset_groups[j]))
					childtwo.setCheckState(0, 0)
						
					# try:
					#     dc[i].compute_statistic('mean', dc[i].subsets[j].components[k], subset_state=dc[i].subsets[j].subset_state)

					# except:
					#     child.setEditable(False)
					#     child.setSelectable(False)
					#     child.setForeground(QtGui.QBrush(Qt.gray)) 

	#                 parent.appendRow(child)
					self.num_rows = self.num_rows + 1
				
	#             grandparent.appendRow(parent)
	#         self.model_components.appendRow(grandparent)
				
	#         # Fill out the dict now that the indices are connected to the QStandardItemModel
	#         for i in range(0, grandparent.rowCount()):
	#             for j in range(0, grandparent.child(i).rowCount()):
	#                 if grandparent.child(i).child(j).row() == 0:
	#                     key = grandparent.child(i).child(j).text() + grandparent.child(i).text()
	#                     self.component_dict[key] = grandparent.child(i).child(j).index()
	#                 else:
	#                     key = grandparent.child(i).child(j).text() + " (" + grandparent.text() + ")" + grandparent.child(i).text()
	#                     self.component_dict[key] = grandparent.child(i).child(j).index()
				
	# def get_layer_artist(self, cls, layer=None, layer_state=None):
	# 	return cls(self.axes, self.state, layer=layer, layer_state=layer_state)


qt_client.add(TutorialDataViewer)