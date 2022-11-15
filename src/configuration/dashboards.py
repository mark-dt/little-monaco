from src.generic_api import GenericApi


class Dashboard(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/dashboards"
        self.folder = "dashboards"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        return super().get_all()

    def get(self, profileId):
        profile = super().get(profileId)
        #profile["rules"].sort(key=self.extract_severity)
        #profile["eventTypeFilters"].sort(key=self.extract_event_type)
        return profile

    def extract_severity(self, json):
        try:
            return json["severityLevel"]
        except KeyError:
            return 0

    def extract_event_type(self, json):
        try:
            return json["predefinedEventFilter"]["eventType"]
        except KeyError:
            return 0

    def download(self):
        return super().download()

    def upload(self):
        super().upload()

    def post(self, custom_event):
        super().post(custom_event)
