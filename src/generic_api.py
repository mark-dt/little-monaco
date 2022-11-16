import os
import logging
import json


class GenericApi:
    def __init__(self, tools, root_url, folder) -> None:
        self.tools = tools
        self.url = root_url
        self.folder = folder
        self.hash_map = {"entityId": [], "hash": []}

    def get_all(self):
        self.tools.logger.debug(f"Downloading {self.folder}")
        res = self.tools.make_request(self.url, method="GET")
        res_json = json.loads(res.text)
        # Iterate through the objects in the array and pop (remove)
        # non user defined custom events
        if "dashboards" in res_json:
            return res_json["dashboards"]
        if "values" not in res_json:
            return []
        if not res_json["values"]:
            return []
        for item in list(res_json["values"]):
            if "id" in item:
                if item["id"].startswith("ruxit.") or item["id"].startswith("dynatrace."):
                    res_json["values"].remove(item)
        return res_json["values"]

    def get(self, profileId):
        self.tools.logger.debug(f"Downloading {self.folder}: {profileId}")
        _url = self.url + "/" + profileId
        res = self.tools.make_request(_url, method="GET")
        hash_string = self.tools.get_hash_from_string(res.text)
        self.hash_map["entityId"].append(profileId)
        self.hash_map["hash"].append(hash_string)
        res_json = json.loads(res.text)
        return res_json

    def upload(self):
        # _profiles_list = dst_dt.getCustomEventsForAlerting()
        self.tools.logger.debug(self.tools.repo)
        _path = os.path.join(self.tools.repo, self.folder)
        if not os.path.isdir(_path):
            self.tools.logger.debug(f"[ERROR] No such folder {_path}")
            return

        self.tools.logger.info(f"Uploading {self.folder}")
        _profiles_list = self.get_all()
        _profiles_names = [self.tools.clean_file_name(n["name"]) for n in _profiles_list]

        try:
            _repo_files = [
                f.split(".")[0]
                for f in os.listdir(_path)
                if f.endswith(".json") and not f.startswith("_map")
            ]
        except Exception as e:
            self.tools.logger.error("Trying to access repo failed {}".format(e))
            return

        # only push new profiles
        _new_porfiles = self.tools.find_new_files(_profiles_names, _repo_files)
        if len(_new_porfiles) < 1:
            self.tools.logger.info(f"No {self.folder} to upload")

        for profile in _new_porfiles:
            profile_json = self.tools.get_json(_path, profile)
            if "name" in profile_json:
                msg = "Uploading {} {}".format(self.folder, profile_json["name"])
            else:
                msg = "Uploading {} {}".format(self.folder, profile_json["displayName"])
            if self.tools.dry_run:
                self.tools.logger.info("[DRY_RUN]" + msg)
            else:
                self.tools.logger.info(msg)
                self.post(profile_json)

    def post(self, custom_event):
        # _url = self.url + '/api/config/v1/anomalyDetection/metricEvents/'
        _payload = json.dumps(custom_event)
        res = self.tools.make_request(self.url, method="POST", payload=_payload)
        return res.status_code

    def download(self):
        self.tools.logger.info("Downloading %s", self.folder)
        entity_list = self.get_all()
        path = self.tools.create_download_folder(self.folder)
        self.tools.logger.debug("%s folder created inside Config Download folder", self.folder)

        # A Nicer, Single-Call Usage
        for entity in self.tools.progress_bar(
            entity_list, prefix="Progress:", suffix="Complete", length=50
        ):
            if "id" in entity:
                entity_id = entity["id"]
            else:
                self.tools.logger.error(f"No ID in entity: {entity}")
                continue

            if 'params' in entity:
                entity_json = self.get(entity_id, entity['params'])
            else:
                entity_json = self.get(entity_id)
            if entity_json is None:
                self.tools.logger.debug("No")
                continue
            if "metadata" in entity_json:
                del entity_json["metadata"]
            if "id" in entity_json:
                del entity_json["id"]

            if "name" in entity:
                name = f"{entity['name']}_{entity_id}"
            else:
                self.tools.logger.error(f"No Name in entity: {entity}")
                continue
            self.tools.store_entity(entity_json, path, name)

        # self.tools.write_hash_map(path, self.hash_map)
