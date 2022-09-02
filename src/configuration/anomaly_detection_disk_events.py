from src.generic_api import GenericApi


class DiskEvent(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/anomalyDetection/diskEvents"
        self.folder = "anomaly-detection-disk-event"
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

    def delete_disk_event(self, diskEventId):
        # RR 2022-02-15: DELETE only on special occasion ;)
        return "404"

        _url = self.url + "/" + diskEventId
        res = self.make_request(_url, method="DELETE")
        return res.status_code
