import logging
import requests
# supress SSL warnings
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.custom_events_for_alerting import CustomEventForAlerting
from src.alerting_profiles import AlertingProfiles
from src.auto_tag import AutoTag
from src.management_zone import ManagementZone
from src.notification import Notification
from src.custom_device import CustomDevice

class DtAPI():

    def __init__(self, tools):
        self.tools = tools
        self.event_for_alerting = CustomEventForAlerting(tools)
        self.alerting_profiles = AlertingProfiles(tools)
        self.auto_tag = AutoTag(tools)
        self.management_zone = ManagementZone(tools)
        self.notification = Notification(tools)
        self.custom_device = CustomDevice(tools)

        if self.tools.download:
            self.download_all()
            return
        
        if self.tools.repo is not None:
            self.upload()


    def get_auto_tags(self):
        return self.auto_tag.get_all()

    def get_single_auto_tag(self, tagId):
        return self.auto_tag.get(tagId)

    def upload(self):
        self.alerting_profiles.upload()
        self.event_for_alerting.upload()
        self.auto_tag.upload()
        self.management_zone.upload()
        self.notification.upload()

    def download_all(self):
        self.custom_device.download()
        self.alerting_profiles.download()
        self.event_for_alerting.download()
        self.auto_tag.download()
        self.management_zone.download()
        self.notification.download()

        
