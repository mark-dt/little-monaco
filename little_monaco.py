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
import re
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

import tools

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
REPO = ''


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
    parser.add_argument('--repo', type=str,
                        help='Repository with environement config')
    parser.add_argument('--environment', '-env', type=str,
                        help='DT environment to work on')
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
    global ROOT_URL, TOKEN, HEADER, DRY_RUN, DOWNLOAD, CMD, REPO
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

    if args.repo is not None:
        REPO = args.repo
    else:
        logging.error('NO REPO DEFINED')
        exit()

    if args.environment not in config:
        logging.error('No valid environment found in config')
        exit()
    # extract ID from URL or use ALIS, maybe use directly a name passed as argument ?
    if 'alias' in config[args.environment]:
        srcEnv = config[args.environment]['alias']
    else:
        srcEnv = extractEnv(config[args.environment]['URL'])

    # TODO: remove dst env ? in future only upload from local to single env in list
    if 'alias' in config['DST-ENV']:
        dstEnv = config['DST-ENV']['alias']
    else:
        dstEnv = extractEnv(config['DST-ENV']['URL'])
        #downloadPathSrc = './download/' + srcEnv
        #downloadPathDst = './download/' + dstEnv

    # cleanup URLs
    tmpUrl = config[args.environment]['URL']
    srcUrl = tmpUrl[:-1] if tmpUrl[-1] == '/' else tmpUrl
    tmpUrl = config['DST-ENV']['URL']
    dstUrl = tmpUrl[:-1] if tmpUrl[-1] == '/' else tmpUrl

    srcDt = Dynatrace(srcUrl, config[args.environment]['token'], './download', srcEnv)
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
    if DRY_RUN:
        logging.info('DRY_RUN')
    return srcDt, dstDt, parameters


# TODO: CHANGE NAME !!
def findNewTags(srcAutoTags, dstAutoTags):
    #srcTagNames = [t['name'] for t in srcAutoTags]
    #dstTagNames = [t['name'] for t in dstAutoTags]
    srcTagNames = srcAutoTags
    dstTagNames = dstAutoTags
    #logging.info(srcTagNames)
    #logging.info(dstTagNames)
    #if len(srcAutoTags) > len(dstAutoTags):
    #    setTagDiff = set(srcTagNames) - set(dstTagNames)
    #else:
    setTagDiff =  set(dstTagNames) - set(srcTagNames)
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


def findCommonCustomEventsForAlerting(srcCustomEventsForAlerting, dstCustomEventsForAlerting):
    srcTagNames = [t['name'] for t in srcCustomEventsForAlerting]
    dstTagNames = [t['name'] for t in dstCustomEventsForAlerting]
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


# TODO: remove or refactor this !!
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

        res = dstDt.pushAutoTag(tag_json)
        if res.status_code > 399:
            logging.error('Could not push auto-tag: %s', res.text)


def uploadNewCustomEventsForAlertingFromLocal(srcDt, dstDt):
    '''read custom events for alerting from local download folder'''
    directory = "CustomEventsForAlerting"
    parent_dir = os.path.join(srcDt.download_folder_path, srcDt.env_name)
    # Custom events for alerting folder Path
    path = os.path.join(parent_dir, directory)
    localCustomEvents = []
    for file_name in [file for file in os.listdir(path) if file.endswith('.json')]:
        with open(path + "\\" + file_name) as json_file:
            localCustomEvents.append(json.load(json_file))

    '''push custom event to dst if it does not exist already'''
    dstCustomEventsForAlerting = dstDt.getCustomEventsForAlerting()
    dstCustomEventsForAlertingNames = []
    for customEvent in dstCustomEventsForAlerting:
        dstCustomEventsForAlertingNames.append(customEvent["name"])
    for customEvent in localCustomEvents:
        if customEvent["name"] not in dstCustomEventsForAlertingNames:
            dstDt.pushCustomEventForAlerting(customEvent)

def upload_custom_events(dst_dt):
    _profiles_list = dst_dt.getCustomEventsForAlerting()
    _profiles_names =[n['name'] for n in _profiles_list]

    _path = os.path.join(REPO, 'custom-events-for-alerting')
    _repo_files = [f.split('.')[0] for f in os.listdir(_path) if f.endswith('.json') and not f.startswith('_map')]

    # only push new profiles
    _new_porfiles = findNewTags(_profiles_names, _repo_files)

    for profile in _new_porfiles:
        profile_json = tools.get_json(_path, profile)
        if DRY_RUN:
            logging.info('DRY_RUN: Uploading Custom Event Alerting %s', profile_json['name'])
        else:
            dst_dt.pushCustomEventForAlerting(profile_json)


def upload_alerting_profiles(dst_dt):
    _profiles_list = dst_dt.getAlertingProfiles()
    _profiles_names =[n['name'] for n in _profiles_list]

    _path = os.path.join(REPO, 'alerting-profile')
    _repo_files = [f.split('.')[0] for f in os.listdir(_path) if f.endswith('.json') and not f.startswith('_map')]

    # only push new profiles
    _new_porfiles = findNewTags(_profiles_names, _repo_files)

    for profile in _new_porfiles:
        profile_json = tools.get_json(_path, profile)
        if DRY_RUN:
            logging.info('DRY_RUN: Uploading Alerting profile %s', profile_json['displayName'])
        else:
            dst_dt.pushAlertingProfile(profile_json)


# should maybe be destination... -> dst_dt
def upload_notifications(src_dt):
    _notification_list = src_dt.getProblemNotifications()
    _notification_names =[n['name'] for n in _notification_list]

    # get destination alerting profiles to check if the prob notificaiton alerting profiles are available on dest
    _alerting_list = src_dt.getAlertingProfiles()
    _alerting_names =[n['name'] for n in _alerting_list]
    #print(_alerting_names)
    #print(_notification_names)
    #onlyfiles = [f for f in os.listdir(mypath) if f.endsWith() isfile(join(mypath, f))]
    #_path = os.path.join(src_dt.download_folder_path, src_dt.env_name, 'notification')
    _path = os.path.join(REPO, 'notification')
    _onlyfiles = [f.split('.')[0] for f in os.listdir(_path) if f.endswith('.json') and not f.startswith('_map')]
    #print(_onlyfiles)
    _new_notification = findNewTags(_notification_names, _onlyfiles)
    # get map from alertin profiles
    #_map_path = os.path.join(src_dt.download_folder_path, src_dt.env_name, 'alerting-profile', '_map.json')
    _map_path = os.path.join(REPO, 'alerting-profile', '_map.json')
    _map_file = open(_map_path)
    _map_json = json.load(_map_file)
    #print(_map_json)
    for _notification in _new_notification:
        # open notification json
        _file_path = os.path.join(_path, _notification + '.json')
        _notification_file = open(_file_path)
        _notification_json = json.load(_notification_file)

        # get alerting_prilfe name from the map
        _alerting_profile_name = _map_json[_notification_json['alertingProfile']]
        # if the alerting profile is not in the destination env then do not porceed furhter
        if _alerting_profile_name not in _alerting_names:
            logging.error('Alertin profile %s, for Notification %s is not in %s', _alerting_profile_name, _notification_json['name'], src_dt.env_name)
            continue
        # find id for of this profile and replace with old
        _profile = [a for a in _alerting_list if a['name'] == _alerting_profile_name][0]
        _notification_json['alertingProfile'] = _profile['id']
        if DRY_RUN:
            logging.info('DRY_RUN: Uploading Notification %s', _notification_json['name'])
        else:
            src_dt.pushProblemNotification(_notification_json)





def downlaodAll(srcDt):
    # download everything
    tools.downloadAutoTags(srcDt)
    tools.downloadDashboards(srcDt)
    tools.downloadAlertingProfiles(srcDt)
    tools.downloadCustomDevices(srcDt)
    tools.downloadProblemNotifications(srcDt)
    tools.downloadApplicationDetectionRules(srcDt)
    tools.downloadCustomEventsForAlerting(srcDt)
    exit()

def uplaod_all(srcDt):
    #upload_notifications(srcDt)
    upload_custom_events(srcDt)
    #upload_alerting_profiles(srcDt)
    exit()

def main():
    '''main'''
    # TODO: change src to dst !!
    srcDt, dstDt, params = init()
    if DOWNLOAD:
        # download everything
        downlaodAll(srcDt)
        #downlaodAll(dstDt)
    #uploadNewTags(srcDt, dstDt)
    uplaod_all(srcDt)
    if CMD == 'updateTags':
        uploadNewTags(srcDt, dstDt)
    elif CMD == 'mergeTags':
        mergeTags(srcDt, dstDt)
    elif CMD == "updateCustomEventsForAlerting":
        uploadNewCustomEventsForAlerting(srcDt, dstDt)
    elif CMD == "updateCustomEventsForAlertingFromLocal":
        uploadNewCustomEventsForAlertingFromLocal(srcDt, dstDt)
    elif CMD == "updateAlertingProfilesFromLocal":
        uploadNewAlertingProfilesFromLocal(srcDt, dstDt)



if __name__ == '__main__':
    main()
