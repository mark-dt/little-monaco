from src.generic_api import GenericApi


class LogMetrics(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/calculatedMetrics/log"
        self.folder = "log-metrics"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        return super().get_all()

    def get(self, metric_id):
        log_metric = super().get(metric_id)
        for filter in log_metric["logSourceFilters"]:
            filter["pathDefinitions"].sort(key=self.extract_definition)
        return log_metric

    def extract_definition(self, json):
        try:
            return json["definition"]
        except KeyError:
            return 0

    def download(self):
        return super().download()

    def upload(self):
        super().upload()
