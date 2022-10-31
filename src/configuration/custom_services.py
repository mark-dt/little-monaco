import json

from src.generic_api import GenericApi
import requests

class CustomService(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + "/api/config/v1/service/customServices/"
        self.folder = "custom-service-old"
        self.technologies = ["dotNet", "java", "go", "nodeJS", "php"]
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        custom_services = []
        for tech in self.technologies:
            tmp = self.url + tech
            res = self.tools.make_request(URL=tmp, method='GET')
            res_json = json.loads(res.text)
            for v in res_json['values']:
                v['params'] = tech
            custom_services.extend(res_json['values'])
        return custom_services

    def get(self, custom_service_id, params):
        tmp = self.url + params + '/' + custom_service_id
        res = self.tools.make_request(URL=tmp, method='GET')
        res_json = json.loads(res.text)
        res_json["rules"].sort(key=self.extract_id)
        return res_json

    def extract_id(self, json):
        try:
            return json["id"]
        except KeyError:
            return 0

    def extract_event_type(self, json):
        try:
            return json["predefinedEventFilter"]["eventType"]
        except KeyError:
            return 0

    def download(self):
        return super().download()
