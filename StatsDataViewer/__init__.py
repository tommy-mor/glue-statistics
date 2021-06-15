import os 

REFRESH_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_refresh.png'))
NOTATION_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_scientific_notation.png'))
EXPORT_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_export.png'))
CALCULATE_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_calculate.png'))
SORT_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_sort.png'))
SETTINGS_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_settings.png'))
INSTRUCTIONS_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_instructions.png'))

HOME_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_home.png'))
SAVE_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_save.png'))
EXPAND_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_expand.png'))
COLLAPSE_LOGO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'glue_collapse.png'))

def setup():
    from .StatsDataViewer import StatsDataViewer
    from glue.config import qt_client
    qt_client.add(StatsDataViewer)
