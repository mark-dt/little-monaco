from src.generic_api import GenericApi


class ManagementZone(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/managementZones"
        self.folder = "management-zone"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        return super().get_all()

    def get(self, mz_id):
        mz_json = super().get(mz_id)
        for rule in mz_json["rules"]:
            rule["propagationTypes"].sort()
        return mz_json

    def download(self):
        return super().download()

    def upload(self):
        super().upload()
