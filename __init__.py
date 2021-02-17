def setup():
    from StatsDataViewer import StatsDataViewer
    from glue.config import qt_client
    qt_client.add(StatsDataViewer)
