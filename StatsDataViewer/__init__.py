def setup():
    from StatsDataViewer import StatsDataViewer
    from glue.config import qt_client
    #stats = StatsDataViewer(data_collection)
    qt_client.add(StatsDataViewer)
