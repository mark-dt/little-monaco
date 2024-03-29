import logging
import requests
import json
import os
import shutil
import datetime
import configparser
import argparse
import threading
import hashlib

# supress SSL warnings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Tools:
    def __init__(self, instance) -> None:
        """
        Initialize logging, parses config file and creates header for requests
        """
        args = self.cmdline_args()
        try:
            args.config = args.config.replace("%userprofile%", os.environ["USERPROFILE"])
        except Exception as e:
            print("{} [ERROR] {}".format(str(datetime.datetime.now())[:-3], e))

        #        print(args.config)
        config_path = args.config
        self.environment = args.environment
        self.lock = threading.Lock()
        self.win_special_chars = '/\\:?"<>|*.'
        self.hash_map_file = "hash_map.txt"

        log_level = args.log_level
        if args.log_level == "DEBUG":
            log_level = logging.DEBUG
        elif args.log_level == "INFO":
            log_level = logging.INFO
        elif args.log_level == "WARNING":
            log_level = logging.WARNING
        elif args.log_level == "ERROR":
            log_level = logging.ERROR
        else:
            log_level = logging.DEBUG

        # care with backslash for unix vs windows paths !
        log_file_name = instance.split("\\")[-1]
        log_file_name = log_file_name.split(".")[0] + ".log"
        if args.log_path is not None:
            tmp_path = args.log_path
            if not os.path.isdir(tmp_path):
                print(
                    "{} [ERROR] Invalid log folder path: {}".format(
                        str(datetime.datetime.now())[:-3], tmp_path
                    )
                )
                exit(-1)
            log_path = os.path.join(tmp_path, log_file_name)
        else:
            log_path = log_file_name
        try:
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s [%(levelname)s] %(message)s",
                handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
            )
        except Exception as e:
            print(
                "{} [ERROR] Couldn't load {}: {}".format(
                    str(datetime.datetime.now())[:-3], log_path, e
                )
            )
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s [%(levelname)s] %(message)s",
                handlers=[logging.StreamHandler()],
            )

        self.logger = logging.getLogger(__name__)

        if args.download:
            self.download_folder = args.download
            self.download = args.download
        else:
            logging.debug("Download was not defined")
            self.download_folder = "../imo-dt-environment-snapshot"
            self.download = True
        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            # config_handle = open(config_path, 'r')
            # config = json.load(config_handle)
        except Exception as exeption:
            logging.error("[%s] Cannot open config %s", exeption, config_path)
            exit(-1)

        self.endpoints = args.endpoints

        try:
            tmp_url = config[args.environment]["url"]
            self.root_url = tmp_url[:-1] if tmp_url[-1] == "/" else tmp_url
            self.token = config[args.environment]["token"]
            logging.debug(self.root_url)
            logging.debug(self.token)
        except Exception as exception:
            logging.error(
                f"[{exception}] Cannot find config {exception}. "
                f"Reading config from {config_path}"
            )
            exit(-1)
        self.header = {
            "Authorization": "Api-TOKEN " + self.token,
            "Content-Type": "application/json",
        }

    def cmdline_args(self):
        """Parse arguments"""
        # Make parser object
        parser = argparse.ArgumentParser(
            description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.add_argument("--endpoints", type=str, help="List of Endpoints to download")
        parser.add_argument(
            "-c",
            "--config",
            type=str,
            help="Path to config (default ./config.ini)",
            # default=f"{os.environ['USERPROFILE']}/IMO/dynatrace.cfg",
        )
        parser.add_argument(
            "--log-level",
            type=str,
            help="Use if you want to have a more verbose output (default INFO)",
            default="INFO",
        )
        parser.add_argument(
            "--log-path", type=str, help="Path to log folder (default ./main.log)", default="./"
        )
        parser.add_argument(
            "-d",
            "--download",
            type=str,
            const="../imo-dt-environment-snapshot",
            help="Download config (default ../imo-dt-environment-snapshot)",
            nargs="?",
        )
        parser.add_argument(
            "-env", "--environment", type=str, required=True, help="Dynatrace Environment"
        )
        return parser.parse_args()

    def make_request(self, URL=None, parameters=None, method=None, payload=None):
        """
        Simplifies making requests

        Parameters:
            URL (str): endpoint for the API call
            parameters (dict): parameters for the POST/PUT requests
            method (str): type of request (POST, PUT, GET, DELETE)
            payload (str): json string of the object to be created/updated

        Returns:
            Request result
        """

        verify_request = False
        try:
            if method == "POST":
                res = requests.post(
                    URL,
                    data=payload,
                    headers=self.header,
                    verify=verify_request,
                    params=parameters,
                    timeout=10,
                )
            elif method == "GET":
                res = requests.get(
                    URL, headers=self.header, verify=verify_request, params=parameters, timeout=10
                )
            elif method == "PUT":
                res = requests.put(
                    URL,
                    data=payload,
                    headers=self.header,
                    verify=verify_request,
                    params=parameters,
                    timeout=10,
                )
            elif method == "DELETE":
                res = requests.delete(URL, headers=self.header, verify=verify_request, timeout=10)
            else:
                logging.error("Unkown Request Method %s", method)
                exit(-1)
        except Exception as exception:
            logging.error(exception)
            raise SystemExit(exception)
        if res.status_code > 399:
            logging.error(res.text)
        return res

    def get_entities(self, entity_selector=None, fields=None, from_="-1w", to="now"):
        url = self.root_url + "/api/v2/entities"
        host_list = []
        parameters = {
            "pageSize": 500,
            "entitySelector": entity_selector,
            "fields": fields,
            "from": from_,
            "to": to,
        }
        res = self.make_request(URL=url, parameters=parameters, method="GET")
        res_json = json.loads(res.text)
        if res.status_code > 399:
            self.logger.error(res.text)
            return host_list
        host_list.extend(res_json["entities"])
        while "nextPageKey" in res_json:
            parameters = {"nextPageKey": res_json["nextPageKey"]}
            res = self.make_request(URL=url, parameters=parameters, method="GET")
            res_json = json.loads(res.text)
            host_list.extend(res_json["entities"])

        return host_list

    def get_problems(self):
        """
        Fetch all Problems affecting Infrastucture components

        Returns:
            Json list of problems
        """
        url = self.root_url + "/api/v2/problems"
        problem_list = []

        params = {
            "from": "now-2w",
            "pageSize": 400,
            "problemSelector": 'impactLevel("INFRASTRUCTURE")',
        }
        res = self.make_request(URL=url, method="GET", parameters=params)
        res_json = json.loads(res.text)
        problem_list.extend(res_json["problems"])
        while "nextPageKey" in res_json:
            parameters = {"nextPageKey": res_json["nextPageKey"]}
            res = self.make_request(url, parameters, "GET")
            res_json = json.loads(res.text)
            problem_list.extend(res_json["problems"])
        # print(res_json['result'])
        return problem_list

    def list_to_string(self, _list):
        return "[%s]" % ", ".join(map(str, _list))

    # return json from specific path + entity
    def get_json(self, _path, entity):
        _file_path = os.path.join(_path, entity + ".json")
        _file = open(_file_path)
        _json = json.load(_file)
        return _json

    def create_download_folder(self, directory):
        # Parent Directory path
        root_dir = os.path.join(self.download_folder, self.environment)
        # parent_dir = os.path.join(root_dir, self.env_alias)
        # Dashboard folder Path
        path = os.path.join(root_dir, directory)
        # create ./download
        if not os.path.isdir(self.download_folder):
            try:
                os.mkdir(self.download_folder)
                logging.debug("Download folder created")
            except Exception as e:
                logging.error(f"Cannot create dir {self.download_folder}")
                exit()
        # create ./download/X-Stage
        if not os.path.isdir(root_dir):
            try:
                os.mkdir(root_dir)
                logging.debug("Download folder created")
            except Exception as e:
                logging.error(f"Cannot create dir {root_dir}")
                exit()
        if os.path.isdir(os.path.join(root_dir, directory)):
            # Delete the exsiting Dashboard
            try:
                shutil.rmtree(path)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
                logging.error("Unable to delete folder " + e.filename + ":" + e.strerror)
        try:
            os.mkdir(path)
            logging.debug(f"Download folder {path} created")
        except Exception as e:
            logging.error(f"Cannot create dir {path}")
            exit()
        return path

    def extract_env_name(self):
        tmp_url = self.root_url.split(".")
        if tmp_url[1] == "sprint" or tmp_url[1] == "live":
            env_name = tmp_url[0][8:]
        # managed ?
        else:
            url = self.root_url.split("/")
            env_name = url[4]
        return env_name

    def clean_file_name(self, file_name):
        for c in self.win_special_chars:
            file_name = file_name.replace(c, "")
        file_name = file_name.replace(" ", "_")
        return file_name

    def write_hash(self, path, jsonString):
        # TODO: used ?
        hash_string = self.get_hash_from_string(jsonString)
        completeName = os.path.join(path, self.hash_map_file)
        file_handle = open(completeName, "a+")
        file_handle.write(hash_string + "\n")
        file_handle.close()

    def write_hash_map(self, path, hash_map):
        completeName = os.path.join(path, self.hash_map_file)
        jsonString = json.dumps(hash_map, sort_keys=True, indent=4)
        file_handle = open(completeName, "a+")
        file_handle.write(jsonString + "\n")
        file_handle.close()

    def get_hash_from_string(self, string):
        hash_object = hashlib.md5(bytes(string, "utf8"))
        return hash_object.hexdigest()

    def check_hash_in_map(self, path, hash):
        completeName = os.path.join(path, self.hash_map_file)
        res = False
        file_handle = open(completeName, "r")
        line_list = file_handle.readlines()
        if hash in line_list:
            res = True

        file_handle.close()
        return res

    def store_entity(self, jsonEntity, path, file_name):
        # lock because of map file writting
        file_name = self.clean_file_name(file_name)
        file_name += ".json"
        complete_name = os.path.join(path, file_name)
        jsonString = json.dumps(jsonEntity, sort_keys=True, indent=4)
        # self.write_hash(path, jsonString)
        try:
            jsonFile = open(complete_name, "w+")
        except Exception as e:
            logging.error("%s", e)
            logging.error("Invalid name %s", complete_name)
            return
        jsonFile.write(jsonString)
        jsonFile.close()
        logging.debug("Created %s", file_name)

    def find_new_files(self, current_files=None, new_files=None):
        srcTagNames = current_files
        dstTagNames = new_files
        setTagDiff = set(dstTagNames) - set(srcTagNames)
        listTagDiff = list(setTagDiff)
        return listTagDiff

    def progress_bar(
        self, iterable, prefix="", suffix="", decimals=1, length=100, fill="█", printEnd="\r"
    ):
        """
        Call in a loop to create terminal progress bar
        @params:
            iterable    - Required  : iterable object (Iterable)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        total = len(iterable)
        if total == 0:
            return

        # Progress Bar Printing Function
        def printProgressBar(iteration):
            # percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            percent = str(iteration) + "/" + str(total)
            filledLength = int(length * iteration // total)
            bar = fill * filledLength + "-" * (length - filledLength)
            print(f"\r{prefix} |{bar}| {percent} {suffix}", end=printEnd)

        # Initial Call
        printProgressBar(0)
        # Update Progress Bar
        for i, item in enumerate(iterable):
            yield item
            printProgressBar(i + 1)
        # Print New Line on Complete
        print()
