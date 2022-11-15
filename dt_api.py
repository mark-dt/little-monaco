# supress SSL warnings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from src.configuration.alerting_profiles import AlertingProfiles
from src.configuration.anomaly_detection_disk_events import DiskEvent
from src.configuration.anomaly_detection_metrics import CustomEventForAlerting
from src.configuration.app_detection_rule import AppDetectionRule
from src.configuration.application_web import ApplicationWeb
from src.configuration.application_web_data_privacy import ApplicationWebDataPrivacy
from src.configuration.auto_tag import AutoTag
from src.configuration.custom_services import CustomService
from src.configuration.extensions import Extensions
from src.configuration.log_metrics import LogMetrics
from src.configuration.management_zone import ManagementZone
from src.configuration.notification import Notification
from src.environment_v2.custom_device import CustomDevice
from src.environment_v2.pg_availability import PGAvailability
from src.environment_v2.pg_rum import PGRUM

from src.environment_v2.schemas import schemas
from src.environment_v2.objects import Object


class DtAPI:
    def __init__(self, tools):
        self.tools = tools

        self.endpoints = []
        self.alerting_profiles = AlertingProfiles(tools)
        self.endpoints.append(self.alerting_profiles)

        self.app_detection_rule = AppDetectionRule(tools)
        self.endpoints.append(self.app_detection_rule)
        self.application_web = ApplicationWeb(tools)
        self.endpoints.append(self.application_web)
        self.application_web_data_privacy = ApplicationWebDataPrivacy(
            tools, self.application_web.get_all()
        )
        self.endpoints.append(self.application_web_data_privacy)
        self.auto_tag = AutoTag(tools)
        self.endpoints.append(self.auto_tag)
        self.custom_device = CustomDevice(tools)
        self.endpoints.append(self.custom_device)
        self.custom_service = CustomService(tools)
        self.endpoints.append(self.custom_service)
        self.disk_event = DiskEvent(tools)
        self.endpoints.append(self.disk_event)
        self.event_for_alerting = CustomEventForAlerting(tools)
        self.endpoints.append(self.event_for_alerting)
        self.extensions = Extensions(tools)
        self.endpoints.append(self.extensions)
        self.log_metrics = LogMetrics(tools)
        self.endpoints.append(self.log_metrics)
        self.management_zone = ManagementZone(tools)
        self.endpoints.append(self.management_zone)
        self.notification = Notification(tools)
        self.endpoints.append(self.notification)
        self.pg_availability = PGAvailability(tools)
        self.endpoints.append(self.pg_availability)
        self.pg_rum = PGRUM(tools)
        self.endpoints.append(self.pg_rum)

        # download all objects defined in schemas
        self.objects = []
        for schema in schemas:
            self.objects.append(Object(tools, schema["id"], schema["folder"]))

        if self.tools.download and self.tools.endpoints:
            self.download_specific_endpoints(self.tools.endpoints)
            return

        if self.tools.download:
            self.download_all()
            return

        if self.tools.repo is not None:
            self.upload()

    def download_specific_endpoints(self, endpoints):
        # comma separated list of endpoints to download
        if ',' not in endpoints:
            #endpoints = endpoints.split(',')
            endpoint_list = [endpoints]
        else:
            endpoint_list = endpoints.split(',')
        self.tools.logger.debug(endpoint_list)
        for endpoint in endpoint_list:
            for ep in self.endpoints:
                if ep.folder == endpoint:
                    ep.download()
        for obj in self.objects:
            for endpoint in endpoint_list:
                if obj.folder == endpoint:
                    obj.download()

    def upload(self):
        # RR 2022-02-15: currently upload - not implemented
        #        self.disk_event.upload()
        #        self.declarative_grouping.upload()

        self.alerting_profiles.upload()
        self.event_for_alerting.upload()
        self.auto_tag.upload()
        self.management_zone.upload()
        self.notification.upload()

    def download_all(self):

        self.alerting_profiles.download()
        self.app_detection_rule.download()
        self.application_web.download()
        self.application_web_data_privacy.download()
        self.auto_tag.download()
        self.custom_device.download()
        self.custom_service.download()
        self.disk_event.download()
        self.event_for_alerting.download()
        self.extensions.download()
        self.log_metrics.download()
        self.management_zone.download()
        self.notification.download()
        for obj in self.objects:
            obj.download()
        # TODO: atm only downloading WEBS
        # self.pg_availability.download()
        # self.pg_rum.download()
