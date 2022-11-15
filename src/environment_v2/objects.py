import logging
import json
from urllib import parse

from src.generic_api import GenericApi


class Object(GenericApi):
    def __init__(self, tools, schema_id, folder) -> None:
        self.tools = tools
        self.page_size = 500
        args = {
            "schemaIds": schema_id,
            "scopes": "environment",
            "fields": "objectId,value",
            "pageSize": self.page_size
        }
        self.url = tools.root_url + "/api/v2/settings/objects?{}".format(parse.urlencode(args))

        self.folder = folder
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        logging.debug(f"Downloading {self.folder}")
        res = self.tools.make_request(self.url, method="GET")
        res_json = json.loads(res.text)
        while "nextPageKey" in res_json:
            _url = self.tools.root_url + "/api/v2/settings/objects"
            _params = {
                "nextPageKey" : res_json["nextPageKey"],
                "pageSize": self.page_size
            }
            res = self.tools.make_request(_url, method="GET", parameters=_params)
            tmp = json.loads(res.text)
            res_json["items"].extend(tmp["items"])

        # Iterate through the objects in the array and pop (remove)
        # non user defined custom events
        if "items" not in res_json:
            return []
        for item in list(res_json["items"]):
            item["id"] = item["objectId"]
            # TODO: extract names of new schemas as needed
            try:
                if "generalProperties" in item["value"]:
                    name = item["value"]["generalProperties"]["name"]
                elif "summary" in item["value"]:
                    name = item["value"]["summary"]
                elif "key" in item["value"]:
                    name = item["value"]["key"]
                elif "displayName" in item["value"]:
                    name = item["value"]["displayName"]
                else:
                    name = item["value"]["name"]
            except Exception as e:
                logging.error(f"{e}: Could not extract name from {item}")
                exit(-1)

            item["name"] = f"{name}"

        self.items = res_json["items"]
        return res_json["items"]

    def get(self, profileId):
        res = [i for i in self.items if i["objectId"] == profileId]
        return res

    def download(self):
        return super().download()
