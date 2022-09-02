import json

from src.generic_api import GenericApi


class ApplicationWebDataPrivacy(GenericApi):
    def __init__(self, tools, app_list) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/applications/web/dataPrivacy"
        self.folder = "application-web-data-privacy"
        self.app_dict = self.generate_app_dict(app_list)
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        return super().get_all()

    def generate_app_dict(self, app_list):
        app_dict = {}
        for app in app_list:
            app_dict[app["id"]] = app["name"]
        return app_dict

    def download(self):
        # print(self.app_list)
        app_dp_list = self.get_all()
        path = self.tools.create_download_folder(self.folder)
        self.tools.logger.info("Downloading %s", self.folder)
        self.tools.logger.debug("%s folder created inside Config Download folder", self.folder)

        for app in app_dp_list:
            name = self.app_dict[app["identifier"]]
            self.tools.store_entity(app, path, name)

    def upload(self):
        super().upload()

    def post(self, custom_event):
        super().post(custom_event)
