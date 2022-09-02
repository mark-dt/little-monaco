from src.generic_api import GenericApi

import json


class PGRUM(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/v2/settings/objects"
        self.folder = "anomaly-detection-process-groups-rum"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        # quering for ALL PGs will take minutes and thousands of API calls...
        selector = "type(process_group),softwareTechnologies(IBM_WEBSPHERE_LIBERTY)"
        return self.tools.get_entities(entity_selector=selector)

    def get(self, profileId):
        _params = {
            "schemaIds": "builtin:rum.processgroup",
            "fields": "objectId,value",
            "scopes": profileId,
        }
        res = self.tools.make_request(URL=self.url, parameters=_params, method="GET")
        res_json = json.loads(res.text)
        if res_json["totalCount"] == 0:
            return None
        else:
            return res_json["items"][0]

    def download(self):
        return super().download()

    def upload(self):
        super().upload()
