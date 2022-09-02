from src.generic_api import GenericApi

import json


class Extensions(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/extensions"
        self.folder = "extensions"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        res = self.tools.make_request(self.url, method="GET")
        res_json = json.loads(res.text)
        extension_list = []
        if "extensions" not in res_json:
            self.tools.logger.debug(f"No Extensions found {res_json}")
            return extension_list
        for extension in res_json["extensions"]:
            extension_list.append(extension["id"])
        extension_config_list = {"entities": []}
        for extension in self.tools.progress_bar(
            extension_list, prefix="Progress:", suffix="Complete", length=50
        ):
            # for extension in extension_list:
            _url = self.tools.root_url + f"/api/config/v1/extensions/{extension}/instances"
            res = self.tools.make_request(_url, method="GET")
            res_json = json.loads(res.text)
            if res_json["totalResults"] < 1:
                continue
            for config in res_json["configurationsList"]:
                id = config["id"]
                _config_url = (
                    self.tools.root_url + f"/api/config/v1/extensions/{extension}/instances/{id}"
                )
                res = self.tools.make_request(_config_url, method="GET")
                res_json = json.loads(res.text)
                extension_config_list["entities"].append(res_json)
        return extension_config_list

    def download(self):
        self.tools.logger.info("Downloading %s", self.folder)
        path = self.tools.create_download_folder(self.folder)
        config_list = self.get_all()
        if "entities" not in config_list:
            return
        for entity in config_list["entities"]:
            # endpoint_name = entity['extensionId'] if 'endpointName' not in entity or entity['endpointName'] == '' else entity['endpointName']
            endpoint_name = entity["extensionId"].split(".")[-1]
            instance_id = entity["endpointId"] if "endpointId" in entity else entity["hostId"]
            name = endpoint_name + "_" + instance_id
            self.tools.store_entity(entity, path, name)
