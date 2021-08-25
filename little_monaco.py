#!/usr/bin/env python3
"""
Short description of the scripts functionality
Example (in your terminal):
    $ python3 little_monaco.py

Author: Mark Bley
Date:	28.06.2021
Version: 0.1
libs: argparse, json, urllib3
"""
import time
import urllib3
import json
import requests
import configparser
import argparse
import os
import shutil
from dt_api import Dynatrace
import logging
logging.basicConfig(
    # level=logging.DEBUG,
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/little_monaco.log"),
        logging.StreamHandler()
    ]
)

# supress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT_URL = ''
TOKEN = ''
HEADER = ''
DRY_RUN = ''
#CMD = ''
DOWNLOAD = False


def cmdline_args():
    '''parse arguments'''
    # Make parser object
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--config', type=str, help='Path to config',
                        default='./config.ini')
    parser.add_argument('-cmd', '--command', type=str,
                        help='e.g. updateTags or mergeTags')
    parser.add_argument('--download', action='store_true',
                        help='Specify what to download', default=False)
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Run without changing anything')
    return parser.parse_args()


def extractEnv(url):
    tmp_url = url.split('.')
    if tmp_url[1] == 'sprint' or tmp_url[1] == 'live':
        env_name = tmp_url[0][8:]
    # managed ?
    else:
        url = url.split('/')
        env_name = url[4]
    return env_name


def init():
    '''initialize parameters'''
    global ROOT_URL, TOKEN, HEADER, DRY_RUN, DOWNLOAD
    parameters = {}
    args = cmdline_args()
    config_path = args.config
    DRY_RUN = args.dry_run
    CMD = args.command
    params = {}
    params['DRY_RUN'] = DRY_RUN
    config = configparser.ConfigParser()
    config.read(config_path)
    HEADER = {
        "Authorization": "Api-TOKEN " + TOKEN,
        "Content-Type": "application/json"
    }


    # extract ID from URL
    srcEnv = extractEnv(config['SRC-ENV']['URL'])
    dstEnv = extractEnv(config['DST-ENV']['URL'])
    #downloadPathSrc = './download/' + srcEnv
    #downloadPathDst = './download/' + dstEnv
    tmpUrl = config['SRC-ENV']['URL']
    srcUrl = tmpUrl[:-1] if tmpUrl[-1] == '/' else tmpUrl
    tmpUrl = config['DST-ENV']['URL']
    dstUrl = tmpUrl[:-1] if tmpUrl[-1] == '/' else tmpUrl
    srcDt = Dynatrace(srcUrl, config['SRC-ENV']['token'], './download', srcEnv)
    dstDt = Dynatrace(dstUrl, config['DST-ENV']['token'], './download', dstEnv)
    # TODO: check that src and dst are not same, check dt got initialized correctly (?)
    #dstDt = Dynatrace(ROOT_URL, TOKEN)

    # TODO: specify API endpoints to download ?
    #downloadList = []
    # if ',' in args.download:
    #    downloadList = args.download.lower().split(',')
    # elif args.download != 'ALL':
    #    downloadList.append(args.download.lower())

    #parameters['downloadList'] = downloadList
    if args.download:
        DOWNLOAD = True
        download = './download'
        if not os.path.isdir(download):
            try:
                os.mkdir(download)
                logging.debug('Download folder created')
            except Exception as e:
                logging.error('Cannot create dir download')
        
        #path = os.path.join(download, srcEnv)

    return srcDt, dstDt, parameters


def findNewTags(srcAutoTags, dstAutoTags):
    srcTagNames = [t['name'] for t in srcAutoTags]
    dstTagNames = [t['name'] for t in dstAutoTags]
    # logging.info(srcTagNames)
    # logging.info(dstTagNames)
    setTagDiff = set(srcTagNames) - set(dstTagNames)
    listTagDiff = list(setTagDiff)
    # logging.info(listTagDiff)
    return listTagDiff


def findCommonTags(srcAutoTags, dstAutoTags):
    srcTagNames = [t['name'] for t in srcAutoTags]
    dstTagNames = [t['name'] for t in dstAutoTags]
    list1_as_set = set(srcTagNames)
    intersection = list1_as_set.intersection(dstTagNames)
    intersection_as_list = list(intersection)
    # logging.info(intersection_as_list)
    return intersection_as_list


def mergeTags(srcDt, dstDt):
    # push only new tags
    srcAutoTags = srcDt.getAutoTags()
    dstAutoTags = dstDt.getAutoTags()
    newTags = findNewTags(srcAutoTags, dstAutoTags)
    newTags = [t for t in srcAutoTags if t['name'] in newTags]
    for tag in newTags:
        t = srcDt.getSingleAutoTag(tag['id'])
        #tag_json = json.loads(t)
        t.pop('metadata')
        t.pop('id')
        dstDt.pushAutoTag(t)

    commonTags = findCommonTags(srcAutoTags, dstAutoTags)
    srcCommonTags = [t for t in srcAutoTags if t['name'] in commonTags]
    dstCommonTags = [t for t in dstAutoTags if t['name'] in commonTags]
    for tag in srcCommonTags:
        raw_tag = srcDt.getSingleAutoTag(tag['id'])
        tag['raw_tag'] = raw_tag

    # sort list of tags to make iteration easier
    srcCommonTags = sorted(srcCommonTags, key=lambda k: k['name'])
    dstCommonTags = sorted(dstCommonTags, key=lambda k: k['name'])

    for i in range(0, len(dstCommonTags)):
        tag = dstDt.getSingleAutoTag(dstCommonTags[i]['id'])
        raw_tag = srcCommonTags[i]['raw_tag']
        # get rid of rules that are already present
        for r2 in tag['rules']:
            i = 0
            while i < len(raw_tag['rules']):
                # for i in range(0, rule_length):
                r1 = raw_tag['rules'][i]
                # compare rules if they are the same
                if hash(json.dumps(r1)) == hash(json.dumps(r2)):
                    raw_tag['rules'].pop(i)
                    # to account for lost place in array
                    i = i - 1
                i = i + 1

        #rules = json.loads(rules)
        if len(raw_tag['rules']) > 0:
            tag['rules'].extend(raw_tag['rules'])
            dstDt.updateTag(tag)

# Maybe not needed since merging also does this ?


def uploadNewTags(srcDt, dstDt):
    '''uploads new tags withou deleting'''
    srcAutoTags = srcDt.getAutoTags()
    dstAutoTags = dstDt.getAutoTags()
    commonTags = findCommonTags(srcAutoTags, dstAutoTags)
    # common tags get deleted and the new ones get uploaded
    tagsToDelte = [t for t in dstAutoTags if t['name'] in commonTags]
    #logging.info('Tags to delete:')
    # logging.info(tagsToDelte)

    for tag in tagsToDelte:
        dstDt.deleteAutoTag(tag['id'])
    time.sleep(2)
    for tag in srcAutoTags:
        tag_json = srcDt.getSingleAutoTag(tag['id'])
        #tag_json = json.loads(t)
        tag_json.pop('metadata')
        tag_id = tag_json['id']
        tag_json.pop('id')

        res = dstDt.pushAutoTag(tag_json)
        while res > 399:
            dstDt.deleteAutoTag(tag_id)
            logging.info('waiting for update...')
            time.sleep(1)
            res = dstDt.pushAutoTag(tag_json)


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


def downloadDashboards(srcDt):
    srcDashboards = srcDt.getDashboards()
    directory = "Dashboards"
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


def downloadAutoTags(srcDt):
    autoTagList = srcDt.getAutoTags()
    directory = "AutoTags"
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
    directory = "AlertingProfiles"
    path = createDownloadDir(srcDt, directory)

    logging.debug('%s folder created inside Config Download folder', directory)
    # print(autoTagList)
    for tag in autoTagList:
        tagJson = srcDt.getSingleAlertingProfile(tag['id'])
        file_name = tagJson["displayName"] + ".json"
        del tagJson['metadata']
        del tagJson['id']
        storeEntity(tagJson, path, file_name)


def downloadCustomDevices(srcDt):
    deviceList = srcDt.getCustomDevices()
    directory = "CustomDevices"
    path = createDownloadDir(srcDt, directory)
    logging.info("Downloading %s", directory)
    logging.debug('%s folder created inside Config Download folder', directory)

    for device in deviceList:
        deviceJson = srcDt.getCustomDevice(device['entityId'])
        file_name = deviceJson["displayName"] + ".json"
        storeEntity(deviceJson, path, file_name)


def downloadProblemNotifications(srcDt):
    deviceList = srcDt.getProblemNotification()
    directory = "ProblemNotifications"
    path = createDownloadDir(srcDt, directory)
    logging.info("Downloading %s", directory)
    logging.debug('%s folder created inside Config Download folder', directory)

    for device in deviceList:
        deviceJson = srcDt.getSingleProblemNotification(device['id'])
        file_name = deviceJson["name"] + ".json"
        storeEntity(deviceJson, path, file_name)


def downloadApplicationDetectionRules(srcDt):
    deviceList = srcDt.getApplicationDetectionRules()
    directory = "ApplicationDetectionRules"
    path = createDownloadDir(srcDt, directory)
    logging.info("Downloading %s", directory)
    logging.debug('%s folder created inside Config Download folder', directory)

    for device in deviceList:
        deviceJson = srcDt.getSingleApplicationDetectionRule(device['id'])
        del deviceJson['metadata']
        del deviceJson['id']
        file_name = device["name"] + ".json"
        storeEntity(deviceJson, path, file_name)


def downlaodAll(srcDt):
    # download everything
    downloadAutoTags(srcDt)
    downloadDashboards(srcDt)
    downloadAlertingProfiles(srcDt)
    downloadCustomDevices(srcDt)
    downloadProblemNotifications(srcDt)
    downloadApplicationDetectionRules(srcDt)


def main():
    '''main'''
    srcDt, dstDt, params = init()
    if DOWNLOAD:
        # download everything
        downlaodAll(srcDt)
        downlaodAll(dstDt)
    #uploadNewTags(srcDt, dstDt)
    # if CMD == 'updateTags':
    #    uploadNewTags(srcDt, dstDt)
    # elif CMD == 'mergeTags':
    #    mergeTags(srcDt, dstDt)
    # elif CMD == "downloadDashboards":
    #    downloadDashboards(srcDt)


if __name__ == '__main__':
    main()
