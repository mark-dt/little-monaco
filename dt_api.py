import logging
import requests
# supress SSL warnings
import urllib3
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Dynatrace():

    def __init__(self, url, token, download_folder_path, env_name):
        self.url = url
        self.token = token
        self.header = {
            "Authorization": "Api-TOKEN " + token,
            "Content-Type": "application/json"
        }
        self.download_folder_path = download_folder_path
        self.env_name = env_name

    def getAutoTags(self):
        logging.debug('Downloading all Tags from {}'.format(self.url))
        _url = self.url + '/api/config/v1/autoTags'
        res = self.make_request(_url, method='GET')
        res_json = json.loads(res.text)
        return res_json['values']

    def getSingleAutoTag(self, tagId):
        _url = self.url + '/api/config/v1/autoTags/' + tagId
        res = self.make_request(_url, method='GET')
        return json.loads(res.text)

    def deleteAutoTag(self, tagId):
        _url = self.url + '/api/config/v1/autoTags/' + tagId
        res = self.make_request(_url, method='DELETE')
        return res.status_code

    def pushAutoTag(self, tag):
        _url = self.url + '/api/config/v1/autoTags'
        logging.info('Uploading new Tag: {}'.format(tag['name']))
        _payload = json.dumps(tag)
        res = self.make_request(_url, method='POST', payload=_payload)
        return res.status_code

    def updateTag(self, tag):
        #TODO: updates the tag with the new passed ruls
        tagId = tag['id']
        logging.info('Updating Tag: {}'.format(tag['name']))
        _url = self.url + '/api/config/v1/autoTags/' + tagId
        _payload = json.dumps(tag)
        self.make_request(_url, method='PUT', payload=_payload)

    def getDashboards(self):
        logging.debug('Downloading all Dashboards from {}'.format(self.url))
        _url = self.url + '/api/config/v1/dashboards'
        res = self.make_request(_url, method='GET')
        res_json = json.loads(res.text)
        if res.status_code > 399:
            print(res.text)
            logging.error(res.text)
        return res_json['dashboards']

    def getSingleDashboard(self, dashboardId):
        logging.debug('Downloading Dashboard {}'.format(dashboardId))
        _url = self.url + '/api/config/v1/dashboards/' + dashboardId
        res = self.make_request(_url, method='GET')
        if res.status_code > 399:
            print(res.text)
            logging.error(res.text)
        return json.loads(res.text)

    def getServiceName(self, svcId):
        print('get svc name')

    def getServiceNameList(self):
        print('get svc name list')

    def getAlertingProfiles(self):
        logging.debug('Downloading alerting profiles')
        _url = self.url + '/api/config/v1/alertingProfiles'
        res = self.make_request(_url, method='GET')
        res_json = json.loads(res.text)
        return res_json['values']

    def getSingleAlertingProfile(self, profileId):
        logging.debug('Downloading alerting profiles')
        _url = self.url + '/api/config/v1/alertingProfiles/' + profileId
        res = self.make_request(_url, method='GET')
        res_json = json.loads(res.text)
        return res_json


    def make_request(self, url, parameters=None, method=None, payload=None):
        '''makes post or get request request'''
        try:
            if method == 'POST':
                res = requests.post(url, data=payload, headers=self.header,
                                    verify=False, params=parameters, timeout=10)
            elif method == 'GET':
                res = requests.get(url, headers=self.header,
                                   verify=False, params=parameters, timeout=10)
            elif method == 'PUT':
                res = requests.put(url, data=payload, headers=self.header,
                                   verify=False, params=parameters, timeout=10)
            elif method == 'DELETE':
                res = requests.delete(
                    url, headers=self.header, verify=False, timeout=10)
            else:
                print('Unkown Method')
                logging.error('Unkown Request Method')
                exit(-1)
        except Exception as exception:
            logging.error(exception)
            raise SystemExit(exception)
        if res.status_code > 399:
            print(res.text)
            logging.error(res.text)
            #exit(-1)
        return res
