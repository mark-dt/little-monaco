import logging
import json
from urllib import parse

from src.generic_api import GenericApi


class LogMetricsv2(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.items = None
        args = {
            "schemaIds": "builtin:logmonitoring.schemaless-log-metric",
            "scopes": "environment",
            "fields": "objectId,value",
        }
        self.url = tools.root_url + "/api/v2/settings/objects?{}".format(parse.urlencode(args))

        self.folder = "log-metric-v2"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        logging.debug(f"Downloading {self.folder}")
        res = self.tools.make_request(self.url, method="GET")
        res_json = json.loads(res.text)
        # Iterate through the objects in the array and pop (remove)
        # non user defined custom events
        if "items" not in res_json:
            return []
        for item in list(res_json["items"]):
            if False and (item["id"].startswith("ruxit.") or item["id"].startswith("dynatrace.")):
                res_json["items"].remove(item)

        self.items = res_json["items"]
        return res_json["items"]

    def get(self, object_id):
        res = [i for i in self.items if i["objectId"] == object_id]
        return res

    def download(self):
        return super().download()
