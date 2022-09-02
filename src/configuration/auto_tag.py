from src.generic_api import GenericApi


class AutoTag(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/autoTags"
        self.folder = "auto-tag"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        return super().get_all()

    def get(self, auto_tag_id):
        auto_tag_json = super().get(auto_tag_id)
        for rule in auto_tag_json["rules"]:
            rule["propagationTypes"].sort()
        return auto_tag_json

    def download(self):
        return super().download()

    def upload(self):
        super().upload()
