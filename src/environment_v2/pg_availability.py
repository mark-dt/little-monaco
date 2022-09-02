from src.generic_api import GenericApi


class PGAvailability(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/anomalyDetection/processGroups"
        self.folder = "anomaly-detection-process-groups"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        # quering for ALL PGs will take minutes and thousands of API calls...
        selector = "type(process_group),softwareTechnologies(IBM_WEBSPHERE_LIBERTY)"
        return self.tools.get_entities(entity_selector=selector)

    def get(self, profileId):
        return super().get(profileId)

    def download(self):
        return super().download()

    def upload(self):
        super().upload()
