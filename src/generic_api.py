import os
import logging
import json


class GenericApi():
    def __init__(self, tools, root_url, folder) -> None:
        self.tools = tools
        self.url = root_url
        self.folder = folder
        self.hash_map = {'entityId': [], 'hash': []}

    def get_all(self):
        logging.debug(f'Downloading {self.folder}')
        res = self.tools.make_request(self.url, method='GET')
        res_json = json.loads(res.text)
        # Iterate through the objects in the array and pop (remove)
        # non user defined custom events
        for item in list(res_json['values']):
            if item["id"].startswith("ruxit.") or item["id"].startswith("dynatrace."):
                res_json['values'].remove(item)

        return res_json['values']

    def get(self, profileId):
        logging.debug(f'Downloading {self.folder}: {profileId}')
        _url = self.url + '/' + profileId
        res = self.tools.make_request(_url, method='GET')
        hash_string = self.tools.get_hash_from_string(res.text)
        self.hash_map['entityId'].append(profileId)
        self.hash_map['hash'].append(hash_string)
        res_json = json.loads(res.text)
        return res_json

    def upload(self):
        #_profiles_list = dst_dt.getCustomEventsForAlerting()
        logging.debug(self.tools.repo)
        _path = os.path.join(self.tools.repo, self.folder)
        if not os.path.isdir(_path):
            logging.debug(f'[ERROR] No such folder {_path}')
            return

        logging.info(f'Uploading {self.folder}')
        _profiles_list = self.get_all()
        _profiles_names = [self.tools.clean_file_name(
            n['name']) for n in _profiles_list]

        try:
            _repo_files = [f.split('.')[0] for f in os.listdir(
                _path) if f.endswith('.json') and not f.startswith('_map')]
        except Exception as e:
            logging.error('Trying to access repo failed {}'.format(e))
            return

        # only push new profiles
        _new_porfiles = self.tools.find_new_files(_profiles_names, _repo_files)
        if len(_new_porfiles) < 1:
            logging.info(f'No {self.folder} to upload')

        for profile in _new_porfiles:
            profile_json = self.tools.get_json(_path, profile)
            if 'name' in profile_json:
                msg = 'Uploading {} {}'.format(
                    self.folder, profile_json['name'])
            else:
                msg = 'Uploading {} {}'.format(
                    self.folder, profile_json['displayName'])
            if self.tools.dry_run:
                logging.info('[DRY_RUN]' + msg)
            else:
                logging.info(msg)
                self.post(profile_json)

    def post(self, custom_event):
        #_url = self.url + '/api/config/v1/anomalyDetection/metricEvents/'
        _payload = json.dumps(custom_event)
        res = self.tools.make_request(
            self.url, method='POST', payload=_payload)
        return res.status_code

    def download(self):
        customEventsList = self.get_all()
        path = self.tools.create_download_folder(self.folder)
        logging.info("Downloading %s", self.folder)
        logging.debug(
            '%s folder created inside Config Download folder', self.folder)

        for customEvent in customEventsList:
            if 'id' in customEvent:
                customEventJson = self.get(customEvent['id'])
            if 'entityId' in customEvent:
                customEventJson = self.get(customEvent['entityId'])

            if 'metadata' in customEventJson:
                del customEventJson['metadata']
            if 'id' in customEventJson:
                del customEventJson['id']

            if 'name' in customEvent:
                name = customEvent['name']
            elif 'displayName' in customEvent:
                name = customEvent['displayName']
            self.tools.store_entity(customEventJson, path, name)
        
        self.tools.write_hash_map(path, self.hash_map)

    def delete_custom_event_for_alerting(self, customEventId):
        _url = self.url + '/' + customEventId
        res = self.make_request(_url, method='DELETE')
        return res.status_code
