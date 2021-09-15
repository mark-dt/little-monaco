import logging
import requests
import json
import os
import shutil
# supress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def make_request(url, parameters=None, method=None, payload=None):
    '''makes post or get request request'''
    try:
        if method == 'POST':
            res = requests.post(url, data=payload, headers=HEADER,
                                verify=False, params=parameters, timeout=10)
        elif method == 'GET':
            res = requests.get(url, headers=HEADER,
                               verify=False, params=parameters, timeout=10)
        elif method == 'PUT':
            res = requests.put(url, data=payload, headers=HEADER,
                                verify=False, params=parameters, timeout=10)
        else:
            print('Unkown Method')
            logging.error('Unkown Request Method')
            exit(-1)
    except requests.exceptions.RequestException as exception:
        logging.error(exception)
        raise SystemExit(exception)
    if res.status_code > 399:
        print(res.text)
        logging.error(res.text)
        exit(-1)
    return res

def storeEntity(jsonEntity, path, fileName):
    completeName = os.path.join(path, fileName)
    jsonString = json.dumps(jsonEntity, sort_keys=True, indent=4)
    try:
        jsonFile = open(completeName, "w")
    except Exception as e:
        logging.error('Invalid name %s', completeName)
        return
    jsonFile.write(jsonString)
    jsonFile.close()
    logging.debug('Created %s', fileName)

def createDownloadDir(srcDt, directory):
    # Parent Directory path
    parent_dir = os.path.join(srcDt.download_folder_path, srcDt.env_name)
    # Dashboard folder Path
    path = os.path.join(parent_dir, directory)
    if not os.path.isdir(parent_dir):
        try:
            os.mkdir(parent_dir)
            logging.debug('Config Download folder created')
        except Exception as e:
            logging.error('Cannot create dir {}'.format(parent_dir))
    else:
        if os.path.isdir(os.path.join(parent_dir, directory)):
            # Delete the exsiting Dashboard
            try:
                shutil.rmtree(path)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
                logging.error("Unable to delete folder " +
                              e.filename + ":" + e.strerror)

    # Create the directory
    # 'Dashboards' in
    #  the corresponding env download folder
    os.mkdir(path)
    return path

def downloadProblemNotifications(srcDt):
    deviceList = srcDt.getProblemNotifications()
    directory = "notification"
    path = createDownloadDir(srcDt, directory)

    #_map = open(path + '/map.json', 'w+')

    logging.info("Downloading %s", directory)
    logging.debug('%s folder created inside Config Download folder', directory)
    for device in deviceList:
        deviceJson = srcDt.getSingleProblemNotification(device['id'])
        file_name = deviceJson["name"] + ".json"
        del deviceJson['id']
        storeEntity(deviceJson, path, file_name)


def downloadDashboards(srcDt):
    srcDashboards = srcDt.getDashboards()
    directory = "dashboard"
    path = createDownloadDir(srcDt, directory)
    logging.info("Downloading %s", directory)
    logging.debug('Dashboards folder created inside Config Download folder')
    for dashboard in srcDashboards:
        dashboardJson = srcDt.getSingleDashboard(dashboard['id'])

        file_name = dashboardJson["dashboardMetadata"]["name"] + ".json"

        try:
            completeName = os.path.join(path, file_name)
        except Exception as e:
            logging.error('Invalid name %s', file_name)
            continue
        del dashboardJson['metadata']
        del dashboardJson['id']
        storeEntity(dashboardJson, path, file_name)
        #jsonString = json.dumps(dashboardJson, sort_keys=True, indent=4)
        #sonFile = open(completeName, "w")
        # jsonFile.write(jsonString)
        # jsonFile.close()
        # logging.debug('Dashboard {} downloaded'.format(
        #    dashboardJson["dashboardMetadata"]["name"]))


def downloadAutoTags(srcDt):
    autoTagList = srcDt.getAutoTags()
    directory = "auto-tag"
    path = createDownloadDir(srcDt, directory)
    logging.info("Downloading %s", directory)
    logging.debug('%s folder created inside Config Download folder', directory)
    for tag in autoTagList:
        tagJson = srcDt.getSingleAutoTag(tag['id'])
        #dashboardJson = srcDt.getSingleDashboard(dashboard['id'])
        file_name = tagJson["name"] + ".json"
        del tagJson['metadata']
        del tagJson['id']
        storeEntity(tagJson, path, file_name)


def downloadAlertingProfiles(srcDt):
    autoTagList = srcDt.getAlertingProfiles()
    directory = "alerting-profile"
    path = createDownloadDir(srcDt, directory)

    logging.debug('%s folder created inside Config Download folder', directory)
    # print(autoTagList)
    _map = {}
    for tag in autoTagList:
        tagJson = srcDt.getSingleAlertingProfile(tag['id'])
        file_name = tagJson["displayName"] + ".json"
        #_map[tagJson['displayName']] = tagJson['id']
        _map[tagJson['id']] = tagJson['displayName']
        del tagJson['metadata']
        del tagJson['id']
        storeEntity(tagJson, path, file_name)
    _map_path = os.path.join(path, '_map.json')
    logging.debug('Creating alertin-profile-map')
    with open(_map_path, 'w', encoding='utf-8') as f:
        json.dump(_map, f, ensure_ascii=False, indent=4)


def downloadCustomDevices(srcDt):
    deviceList = srcDt.getCustomDevices()
    directory = "custom device"
    path = createDownloadDir(srcDt, directory)
    logging.info("Downloading %s", directory)
    logging.debug('%s folder created inside Config Download folder', directory)

    for device in deviceList:
        deviceJson = srcDt.getCustomDevice(device['entityId'])
        file_name = deviceJson["displayName"] + ".json"
        storeEntity(deviceJson, path, file_name)


def downloadApplicationDetectionRules(srcDt):
    deviceList = srcDt.getApplicationDetectionRules()
    directory = "app-detection-rule"
    path = createDownloadDir(srcDt, directory)
    logging.info("Downloading %s", directory)
    logging.debug('%s folder created inside Config Download folder', directory)

    for device in deviceList:
        deviceJson = srcDt.getSingleApplicationDetectionRule(device['id'])
        del deviceJson['metadata']
        del deviceJson['id']
        file_name = device["name"] + ".json"
        storeEntity(deviceJson, path, file_name)


def downloadCustomEventsForAlerting(srcDt):
    customEventsList = srcDt.getCustomEventsForAlerting()
    directory = "custom-events-for-alerting"
    path = createDownloadDir(srcDt, directory)
    logging.info("Downloading %s", directory)
    logging.debug('%s folder created inside Config Download folder', directory)

    for customEvent in customEventsList:
        customEventJson = srcDt.getSingleCustomEventForAlerting(customEvent['id'])
        del customEventJson['metadata']
        del customEventJson['id']
        #customEvent["name"] = re.sub("[/:*?\"<>|]","",customEvent["name"])
        customEvent["name"].replace("\\", "")
        file_name = customEvent["name"] + ".json"
        storeEntity(customEventJson, path, file_name)

# return json from specific path + entity
def get_json(_path, entity):
    _file_path = os.path.join(_path, entity + '.json')
    _file = open(_file_path)
    _json = json.load(_file)
    return _json