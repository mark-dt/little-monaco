from src.generic_api import GenericApi


class ApplicationWeb(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/applications/web"
        self.folder = "application-web"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        return super().get_all()

    def get(self, web_id):
        return super().get(web_id)

    def download(self):
        return super().download()

    def upload(self):
        super().upload()

    def post(self, custom_event):
        super().post(custom_event)
