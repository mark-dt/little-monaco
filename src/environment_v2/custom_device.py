import json

from src.generic_api import GenericApi


class CustomDevice(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/v2/entities"
        self.folder = "custom-device"
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        selector = 'type("CUSTOM_DEVICE")'
        fields = "+properties.customProperties,+fromRelationships,+properties.detectedName"
        entities = self.tools.get_entities(selector, fields)
        for e in entities:
            e["id"] = e["entityId"]
            e["name"] = e["properties"]["detectedName"]
        return entities

    def get(self, device_id):
        url = self.url + "/" + device_id
        res = self.tools.make_request(url, method="GET")
        res_json = json.loads(res.text)
        del res_json["lastSeenTms"]
        res_json["tags"].sort(key=self.extract_key)
        # res_json['id'] = res_json["entityId"]
        return res_json

    def extract_key(self, json):
        try:
            return json["stringRepresentation"]
        except KeyError:
            return 0

    def download(self):
        return super().download()

    def upload(self):
        super().upload()

    def post(self, custom_event):
        super().post(custom_event)
