from src.generic_api import GenericApi


class CustomEventForAlerting(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/anomalyDetection/metricEvents"
        self.folder = "anomaly-detection-metrics"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        return super().get_all()

    def get(self, profileId):
        return super().get(profileId)

    def download(self):
        return super().download()

    def upload(self):
        super().upload()

    def post(self, custom_event):
        super().post(custom_event)
