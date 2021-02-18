import os
import time
import numpy as np
import sys
import pandas as pd
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
from glue.core import DataCollection, Hub, HubListener, Data, coordinates
from glue.core.link_helpers import LinkSame
from glue.core.message import DataMessage, DataCollectionMessage, SubsetMessage, SubsetUpdateMessage
import pandas as pd
from pandas import DataFrame
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from glue.icons.qt import helpers
from PyQt5 import QtCore, QtWidgets, QtGui
from qtpy import compat
from glue_vispy_viewers.volume.volume_viewer import VispyVolumeViewer
from glue.core.message import DataMessage, DataCollectionMessage, SubsetMessage, LayerArtistUpdatedMessage, NumericalDataChangedMessage
from IPython.display import display, HTML
from PyQt5.QtGui import *
from glue.config import auto_refresh
auto_refresh(True)
import glue.core.data_collection
from glue import custom_viewer


image_filename = '/Users/jk317/Glue/w5.fits'
catalog_filename = '/Users/jk317/Glue/w5_psc.vot'

####load 2 datasets from files
catalog = load_data(catalog_filename)
image = load_data(image_filename)
xc = DataCollection([catalog,image])
### link positional information
xc.add_link(LinkSame(catalog.id['RAJ2000'], image.id['Right Ascension']))
xc.add_link(LinkSame(catalog.id['DEJ2000'], image.id['Declination']))

####Create subset based on filament mask
ra_state = (image.id['Right Ascension'] > 44) & (image.id['Right Ascension'] < 46)
subset_group = xc.new_subset_group('Subset 1', ra_state)
subset_group.style.color = '#FF0000'

de_state = image.id['Declination'] > 60
subset_group1 = xc.new_subset_group('Subset 2', de_state)
subset_group1.style.color = '#00FF00'

j_state = catalog.id['Jmag'] > 14
subset_group2 = xc.new_subset_group('Jmag Selection', j_state)
subset_group2.style.color = '#00FF00'


@viewer_tool
class convertNotation(CheckableTool):
	icon = '/Users/jk317/Glue/icons/glue_calculate.png'
	tool_id = 'notation_tool'
	action_text = 'Convert'
	tool_tip = 'Click icon to toggle Scientific noation or decimal'
	status_tip = 'Click to toggle notation'
	shortcut = 'N'

	def __init__(self,viewer):
		self.viewer = viewer

	def activate(self):
		print("Convert button activate")
		data_labels = self.data_frame['Dataset']
		comp_labels = self.data_frame['Component']
		subset_labels = self.data_frame['Subset']

		mean_vals = []
		median_vals = []
		min_vals = []
		max_vals = []
		sum_vals = []

		if self.stan_notation.isChecked():
			self.isSci = False
			# Build string to format in standard notation
			string = "%." + str(self.num_sigs) + 'F'
		else:
			self.isSci = True
			# Build string to format in scientific notation
			string = "%." + str(self.num_sigs) + 'E'



		for i in range(0, len(self.data_frame)):
			# Traverse through the dataframe and get the names of the component, dataset, and subset
			component = self.data_frame['Component'][i]
			dataset = self.data_frame['Dataset'][i]
			subset = self.data_frame['Subset'][i]

			# Pull the correct index of the data in data_accurate
			idx_c = np.where(component == self.data_accurate['Component'])
			idx_d = np.where(dataset == self.data_accurate['Dataset'])
			idx_s = np.where(subset == self.data_accurate['Subset'])
			idx1 = np.intersect1d(idx_c, idx_d)
			idx2 = np.intersect1d(idx1, idx_s)[0]

			# Format the data in data_accurate
			mean_vals.append(string % Decimal(self.data_accurate['Mean'][idx2]))
			median_vals.append(string % Decimal(self.data_accurate['Median'][idx2]))
			min_vals.append(string % Decimal(self.data_accurate['Minimum'][idx2]))
			max_vals.append(string % Decimal(self.data_accurate['Maximum'][idx2]))
			sum_vals.append(string % Decimal(self.data_accurate['Sum'][idx2]))

		# Build the column_data and update the data_frame
		column_data = np.asarray([subset_labels, data_labels, comp_labels, mean_vals, median_vals, min_vals, max_vals, sum_vals]).transpose()
		self.data_frame = pd.DataFrame(column_data, columns=self.headings)
		model = pandasModel(self.data_frame, xc)
		self.table.setModel(model)
		self.table.setSortingEnabled(True)
		self.table.setShowGrid(False)


	def close(self):
		pass


@viewer_tool
class ExportButton(Tool):
	icon = '/Users/jk317/Glue/icons/export.png'
	tool_id = 'export_tool'
	action_text = 'Export'
	tool_tip = 'Click icon to export'
	status_tip = 'Click to export'
	shortcut = 'F'

	def __init__(self,viewer):
		self.viewer = viewer

	def activate(self):
		print("Export button activate")
		self.viewer.pressedEventExport()
		#print(self.viewer.layers[0].layer)

	def close(self):
		pass

@viewer_tool
class HomeButton(Tool):

	icon = 'glue_home'
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

	icon = '/Users/jk317/Glue/icons/glue_hierarchy.png'
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

	icon = '/Users/jk317/Glue/icons/glue_expand.png'
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

	icon = '/Users/jk317/Glue/icons/glue_calculate.png'
	tool_id = 'calc_tool'
	action_text = 'Calculate'
	tool_tip = 'Click side icons to calculate'
	status_tip = 'Click to calculate'
	shortcut = 'C'

	def __init__(self, viewer):
		self.viewer = viewer

	def activate(self):
		print("Calculate button activate")
		self.viewer.pressedEventCalculate()
		print(self.viewer.layers[0].layer)

	def close(self):
		pass

@viewer_tool
class SortButton(CheckableTool):

	icon = '/Users/jk317/Glue/icons/glue_sort.png'
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


	expandAll = CallbackProperty(False, docstring='The button which expands or collapses all items')
	decPlaces = CallbackProperty()

	numNotation = CallbackProperty(False, docstring='The button which changes number notation')

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
	tools = ['home_tool', 'move_tool', 'calc_tool', 'sort_tool', 'notation_tool','export_tool'] #  'expand_tool'



	def __init__(self, *args, **kwargs):
		super(StatsDataViewer, self).__init__(*args, **kwargs)

		# dc = DataCollection()
		self.no_update = True
		self.calculatedList = np.array(["Subset,Dataset,Component,Mean,Median,Minimum,Maximum,Sum"])

		self.headings = ('Name', 'Mean', 'Median', 'Minimum', 'Maximum', 'Sum')

		# Set up dicts for row indices
		self.subset_dict = dict()
		self.component_dict = dict()

		self.selected_dict = dict()
		self.selected_indices = []


		# Set up tree widget item
		self.nestedtree = QTreeWidget(self)
		self.nestedtree.setSelectionMode(QAbstractItemView.NoSelection)


		self.nestedtree.setColumnCount(6)
		# self.nestedtree.setColumnHidden(6, True)
		self.nestedtree.setColumnWidth(0, 250)
		self.nestedtree.header().setSortIndicator(1, 0)

		self.isSci = True
		self.num_sigs = 3

		# Set up past selected items
		self.past_selected = []

		#self.headings =
		QTreeWidget.setHeaderLabels(self.nestedtree, self.headings)
		self.axes = plt.subplot(1, 1, 1)
		self.setCentralWidget(self.nestedtree)


		# # Set component_mode to false, default is subset mode
		self.component_mode = False

		# # These will only be true when the treeview has to switch between views and a
		# # Change has been made in the other
		self.updateSubsetSort = False
		self.updateComponentSort = False

		# Sort by subsets as a default
		self.sortBySubsets()


		# Set up dict for caching
		self.cache_stash = dict()


		self.nestedtree.clearSelection()


		self.state.add_callback('expandAll', self.expandAll)
		# self.state.add_callback('sort_by', self.convertNotation)
		self.state.add_callback('decPlaces', self.decPlaces)
		self.state.add_callback('numNotation', self.convertNotation)

		print(self.state.layers)

		print(self.layers)


		self.data__ = self.dataList()
		print(self.data__)

	def initialize_toolbar(self):
		super(StatsDataViewer, self).initialize_toolbar()
		BasicToolbar.setContextMenuPolicy(self,Qt.PreventContextMenu)


	def myPressedEvent(self, currentQModelIndex):
		pass


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

		newly_selected = np.setdiff1d(self.selected_indices, self.past_selected)


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
			for col_index in range (0, len(new_data)):
				if (col_index > 0):
					print("xxxxxx")
					print(new_data[col_index])
					self.nestedtree.itemFromIndex(newly_selected[index]).setData(col_index, 0, new_data[col_index])

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
					idx_c = np.where(self.data_frame['Component'] == xc[data_i].components[comp_i].label)
					idx_d = np.where(self.data_frame['Dataset'] == xc[data_i].label)
					idx_s = np.where(self.data_frame['Subset'] == xc[data_i].subsets[subset_i].label)
					idx1 = np.intersect1d(idx_c, idx_d)
					idx2 = np.intersect1d(idx1, idx_s)

					self.data_frame = self.data_frame.drop(idx2)
				except:
					pass

			else:
				try:
				# Find the index in the table of the unchecked element, if it's in the table

					# Find the matching component and dataset indices and intersect them to get the unique index
					idx_c = np.where(self.data_frame['Component'] == xc[data_i].components[comp_i].label)
					idx_d = np.where(self.data_frame['Dataset'] == xc[data_i].label)
					idx_s = np.where(self.data_frame['Subset'] == '--')
					idx1 = np.intersect1d(idx_c, idx_d)
					idx2 = np.intersect1d(idx1, idx_s)

					# self.data_frame = self.data_frame.drop(idx2)
				except:
					pass

		# Update the past selected indices
		self.past_selected = self.selected_indices


	def pressedEventCalculate(self):
		'''
		Every time the selection in the treeview changes:
		if it is newly selected, add it to the table
		if it is newly deselected, remove it from the table
		'''

		# Get the indexes of all the selected components
		self.selected_indices = []

		print(self.selected_indices)
		print("000002")

		# create list of rows to calculate
		if not self.component_mode:

			for data_i in range (0, len(xc)):

				for comp_i in range (0, len(xc[data_i].components)):

					# if checked, add to selected list
					if self.nestedtree.invisibleRootItem().child(0).child(data_i).child(comp_i).checkState(0) or self.nestedtree.invisibleRootItem().child(0).child(data_i).checkState(0) or self.nestedtree.invisibleRootItem().child(0).checkState(0):
						self.selected_indices.append(
							self.nestedtree.indexFromItem(self.nestedtree.invisibleRootItem().child(0).child(data_i).child(comp_i)))
					else:
						pass

			for subset_i in range (0, len(xc.subset_groups)):

				for data_i in range (0, len(xc)):

					for comp_i in range (0, len(xc[data_i].components)):
						# print("xoxoxo")
						# print (self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).child(comp_i))
						if self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).child(comp_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).child(subset_i).checkState(0) or self.nestedtree.invisibleRootItem().child(1).checkState(0):
							print("lalalal")
							self.selected_indices.append(
								self.nestedtree.indexFromItem(self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).child(comp_i)))

		else:
			for data_i in range(0,len(xc)):

				# subset_i and comp_i are switched by accident
				for subset_i in range(0, len(xc[data_i].components)):

					for comp_i in range(0, len(xc.subset_groups) + 1):

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
				self.calculatedList = np.append(self.calculatedList, new_data[col_index])
				if (col_index > 2):
					print("xxxxxx")
					print(new_data[col_index])
					self.nestedtree.itemFromIndex(newly_selected[index]).setData(col_index-2, 0, new_data[col_index])



	def itemMasterList(self):

		item_Master_List = []

		# create list of rows to calculate
		if not self.component_mode:

			item_Master_List.append(self.nestedtree.invisibleRootItem().child(0))

			for data_i in range (0, len(xc)):

				item_Master_List.append(self.nestedtree.invisibleRootItem().child(0).child(data_i))

				for comp_i in range (0, len(xc[data_i].components)):

					item_Master_List.append(self.nestedtree.invisibleRootItem().child(0).child(data_i).child(comp_i))

			item_Master_List.append(self.nestedtree.invisibleRootItem().child(1))

			for subset_i in range (0, len(xc.subset_groups)):

				item_Master_List.append(self.nestedtree.invisibleRootItem().child(1).child(subset_i))

				for data_i in range (0, len(xc)):

					item_Master_List.append(self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i))

					for comp_i in range (0, len(xc[data_i].components)):

						item_Master_List.append(self.nestedtree.invisibleRootItem().child(1).child(subset_i).child(data_i).child(comp_i))


		else:

			for data_i in range(0, len(xc)):

				item_Master_List.append(self.nestedtree.invisibleRootItem().child(data_i))

				for comp_i in range(0, len(xc[data_i].components)):

					item_Master_List.append(self.nestedtree.invisibleRootItem().child(data_i).child(comp_i))

					for subset_i in range(0, len(xc.subset_groups) + 1):

						item_Master_List.append(self.nestedtree.invisibleRootItem().child(data_i).child(comp_i).child(subset_i))


		return item_Master_List


	def pressedEventExport(self):

		file_name, fltr = compat.getsavefilename(caption="Choose an output filename")
		try:
			df = pd.DataFrame(self.calculatedList)
			df.to_csv(str(file_name), header=None ,index=None)
			print("asdfasdf")
			print(df)
		except:
			print("Export failed ")

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
		self.pressedEventCalculate()

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
		self.pressedEventCalculate()

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
		data_label = xc[data_i].label
		comp_label = xc[data_i].components[comp_i].label # add to the name array to build the table

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

		mean_val = string % column_data[3]
		print(mean_val)
		print("mean_val ^^")
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
		print("newDataStats triggered")
		# Generates new data for a dataset that has to be calculated

		subset_label = "--"
		data_label = xc[data_i].label
		comp_label = xc[data_i].components[comp_i].label # add to the name array to build the table

		# Build the cache key
		cache_key = subset_label + data_label + comp_label

		# Find the stat values
		# Save the data in the cache
		mean_val = xc[data_i].compute_statistic('mean', xc[data_i].components[comp_i])
		median_val = xc[data_i].compute_statistic('median', xc[data_i].components[comp_i])
		min_val = xc[data_i].compute_statistic('minimum', xc[data_i].components[comp_i])
		max_val = xc[data_i].compute_statistic('maximum', xc[data_i].components[comp_i])
		sum_val = xc[data_i].compute_statistic('sum', xc[data_i].components[comp_i])

		column_data = (subset_label, data_label, comp_label, mean_val, median_val, min_val, max_val, sum_val)

		self.cache_stash[cache_key] = column_data

		return column_data

	def runSubsetStats (self, subset_i, data_i, comp_i):
		'''
		Runs statistics for the subset subset_i with respect to the component comp_i of data set data_i
		'''

		subset_label = xc[data_i].subsets[subset_i].label
		data_label = xc[data_i].label
		comp_label = xc[data_i].components[comp_i].label # add to the name array to build the table

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
		print(mean_val)
		print("mean_val ^")
		median_val = string % column_data[4]
		min_val = string % column_data[5]
		max_val = string % column_data[6]
		sum_val = string % column_data[7]

		# Create the column data array and append it to the data frame
		column_data = (subset_label, data_label, comp_label, mean_val, median_val, min_val, max_val, sum_val)
		return column_data

	def newSubsetStats(self, subset_i, data_i, comp_i):
		# Generates new data for a subset that needs to be calculated
		subset_label = xc[data_i].subsets[subset_i].label
		data_label = xc[data_i].label
		comp_label = xc[data_i].components[comp_i].label # add to the name array to build the table

		# Build the cache key
		cache_key = subset_label + data_label + comp_label

		mean_val = xc[data_i].compute_statistic('mean', xc[data_i].subsets[subset_i].components[comp_i], subset_state=xc[data_i].subsets[subset_i].subset_state)
		median_val = xc[data_i].compute_statistic('median', xc[data_i].subsets[subset_i].components[comp_i], subset_state=xc.subset_groups[subset_i].subset_state)
		min_val = xc[data_i].compute_statistic('minimum', xc[data_i].subsets[subset_i].components[comp_i], subset_state=xc.subset_groups[subset_i].subset_state)
		max_val = xc[data_i].compute_statistic('maximum', xc[data_i].subsets[subset_i].components[comp_i], subset_state=xc.subset_groups[subset_i].subset_state)
		sum_val = xc[data_i].compute_statistic('sum', xc[data_i].subsets[subset_i].components[comp_i], subset_state=xc.subset_groups[subset_i].subset_state)

		column_data = (subset_label, data_label, comp_label, mean_val, median_val, min_val, max_val, sum_val)

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


	def generateSubsetView(self):
		self.component_mode = False
		self.model_subsets = QStandardItemModel()
		self.model_subsets.setHorizontalHeaderLabels([''])

		dataItem =  QTreeWidgetItem(self.nestedtree)
		dataItem.setData(0, 0, '{}'.format('Data'))
		# dataItem.setExpanded(True)
		dataItem.setCheckState(0, 0)


		for i in range(0, len(xc)):

			parentItem = QTreeWidgetItem(dataItem)
			parentItem.setCheckState(0, 0)
			parentItem.setData(0, 0, '{}'.format(xc.labels[i]))
			parentItem.setIcon(0, helpers.layer_icon(xc[i]))

			# Make all the data components be children, nested under their parent
			for j in range(0,len(xc[i].components)):

				childItem = QTreeWidgetItem(parentItem)
				childItem.setCheckState(0, 0)
				childItem.setData(0, 0, '{}'.format(str(xc[i].components[j])))
				childItem.setIcon(0, helpers.layer_icon(xc[i]))

				# Add to the subset_dict
				key = xc[i].label + xc[i].components[j].label + "All data-" + xc[i].label


				self.num_rows = self.num_rows + 1



		subsetItem = QTreeWidgetItem(self.nestedtree)
		subsetItem.setData(0, 0, '{}'.format('Subsets'))
		subsetItem.setCheckState(0, 0)

		for j in range(0, len(xc.subset_groups)):

			grandparent = QTreeWidgetItem(subsetItem)
			grandparent.setData(0, 0, '{}'.format(xc.subset_groups[j].label))
			grandparent.setIcon(0, helpers.layer_icon(xc.subset_groups[j]))
			grandparent.setCheckState(0, 0)

			for i in range(0, len(xc)):

				parent = QTreeWidgetItem(grandparent)
				parent.setData(0, 0, '{}'.format(xc.subset_groups[j].label) + ' (' + '{}'.format(xc[i].label) + ')')

				parent.setIcon(0, helpers.layer_icon(xc.subset_groups[j]))
				parent.setCheckState(0, 0)


				for k in range(0, len(xc[i].components)):

					child = QTreeWidgetItem(parent)
					child.setData(0, 0, '{}'.format(str(xc[i].components[k])))
					# child.setEditable(False)
					child.setIcon(0, helpers.layer_icon(xc.subset_groups[j]))
					child.setCheckState(0, 0)

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


	def generateComponentView(self):
		self.component_mode = True

		for i in range(0,len(xc)):

			grandparent = QTreeWidgetItem(self.nestedtree)
			grandparent.setData(0, 0, '{}'.format(xc.labels[i]))
			grandparent.setIcon(0, helpers.layer_icon(xc[i]))
			grandparent.setCheckState(0, 0)

			for k in range(0,len(xc[i].components)):
				parent = QTreeWidgetItem(grandparent)
				parent.setData(0, 0, '{}'.format(str(xc[i].components[k])))
				parent.setCheckState(0, 0)

				child = QTreeWidgetItem(parent)
				child.setData(0, 0, '{}'.format('All data (' + xc.labels[i] + ')'))
				child.setIcon(0, helpers.layer_icon(xc[i]))
				child.setCheckState(0, 0)

				self.num_rows = self.num_rows + 1

				for j in range(0, len(xc.subset_groups)):
					childtwo = QTreeWidgetItem(parent)
					childtwo.setData(0, 0, '{}'.format(xc.subset_groups[j].label))
					# child.setEditable(False)
					childtwo.setIcon(0, helpers.layer_icon(xc.subset_groups[j]))
					childtwo.setCheckState(0, 0)


					self.num_rows = self.num_rows + 1




qt_client.add(StatsDataViewer)
