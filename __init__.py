def setup(data_collection):
    from Statdata_collectionsDataViewer import StatsDataViewer
    from glue.config import qt_client
    stats = StatsDataViewer(data_collection)
    qt_client.add(stats)
