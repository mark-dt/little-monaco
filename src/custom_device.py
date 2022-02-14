import json

from src.generic_api import GenericApi

class CustomDevice(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + '/api/v2/entities'
        self.folder = 'custom-device'
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        selector = 'type("CUSTOM_DEVICE"),tag("device_type")'
        fields = '+properties.customProperties,+fromRelationships'
        return self.tools.get_entities(selector, fields)

    def get(self, device_id):
        url = self.url + '/' + device_id
        res = self.tools.make_request(url, method='GET')
        res_json = json.loads(res.text)
        return res_json

    def download(self):
        return super().download()

    def upload(self):
        super().upload()

    def post(self, custom_event):
        super().post(custom_event)


    def delete_custom_event_for_alerting(self, customEventId):
        _url = self.url + '/' + customEventId
        res = self.tools.make_request(_url, method='DELETE')
        return res.status_code