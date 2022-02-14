import os
import logging
import json

from src.generic_api import GenericApi

class AlertingProfiles(GenericApi):
    def __init__(self, tools) -> None:
        self.tools = tools
        self.url = tools.root_url + '/api/config/v1/alertingProfiles'
        self.folder = 'alerting-profiles'
        #super().__init__(self, tools, self.url, self.folder)
        GenericApi.__init__(self, tools, self.url, self.folder)

    def get_all(self):
        return super().get_all()

    def get(self, profileId):
        return super().get(profileId)

    def download(self):
        return super().download()

    def upload(self):
        super().upload()

    def post(self, custom_event):
        super().post(custom_event)

    def delete_custom_event_for_alerting(self, customEventId):
        _url = self.url + '/' + customEventId
        res = self.make_request(_url, method='DELETE')
        return res.status_code