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
