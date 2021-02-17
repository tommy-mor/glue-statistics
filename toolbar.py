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
from glue.core.message import DataMessage, DataCollectionMessage, SubsetMessage, SubsetUpdateMessage, \
	LayerArtistUpdatedMessage, NumericalDataChangedMessage, DataUpdateMessage
import pandas as pd
from pandas import DataFrame
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from glue.icons.qt import helpers
from PyQt5 import QtCore, QtWidgets, QtGui
from qtpy import compat
from PyQt5.QtGui import *
from glue.config import auto_refresh
auto_refresh(True)
import glue.core.data_collection
from glue import custom_viewer




@viewer_tool
class convertNotation(CheckableTool):
	icon = '/icons/glue_calculate.png'
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
	icon = '/icons/glue_export.png'
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

	icon = '/icons/glue_hierarchy.png'
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

	icon = '/glue_expand.png'
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

	icon = '/icons/glue_calculate.png'
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

	icon = '/icons/glue_sort.png'
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
