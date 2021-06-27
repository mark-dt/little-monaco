#!/usr/bin/env python3
"""
Short description of the scripts functionality
Example (in your terminal):
    $ python3 template.py --stage A

Author: <Your Name>
Date:	dd.mm.yyyy
Version: 0.1
libs: argparse, json, urllib3
"""
from dt_api import Dynatrace
import logging
import argparse
import configparser
import requests
# supress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


ROOT_URL = ''
TOKEN = ''
HEADER = ''
DRY_RUN = ''


def cmdline_args():
    '''parse arguments'''
    # Make parser object
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--stage', required=True,
                        type=str, help='A oder E')
    parser.add_argument('-c', '--config', type=str, help='Path to config',
                        default='./config.ini')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='Run without changing anything')
    return parser.parse_args()


def init():
    '''initialize parameters'''
    global ROOT_URL, TOKEN, HEADER, DRY_RUN
    args = cmdline_args()
    config_path = args.config
    stage = args.stage
    DRY_RUN = args.dry_run

    params = {}
    params['DRY_RUN'] = DRY_RUN
    config = configparser.ConfigParser()
    config.read(config_path)
    HEADER = {
        "Authorization": "Api-TOKEN " + TOKEN,
        "Content-Type": "application/json"
    }

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/main.log"),
            logging.StreamHandler()
        ]
    )

    srcDt = Dynatrace(config['SRC-ENV']['URL'], config['SRC-ENV']['token'])
    dstDt = Dynatrace(config['DST-ENV']['URL'], config['DST-ENV']['token'])
    # TODO: check that src and dst are not same, check dt got initialized correctly (?)
    #dstDt = Dynatrace(ROOT_URL, TOKEN)
    return srcDt, dstDt


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


def uploadNewTags(srcDt, dstDt):
    '''uploads new tags withou deleting'''
    srcAutoTags = srcDt.getAutoTags()
    dstAutoTags = dstDt.getAutoTags()
    commonTags = findCommonTags(srcAutoTags, dstAutoTags)
    # common tags get deleted and the new ones get uploaded
    tagsToDelte = [t for t in dstAutoTags if t['name'] in commonTags]
    #logging.info(tagsToDelte)

    for tag in tagsToDelte:
        dstDt.deleteAutoTag(tag['id'])

    for tag in srcAutoTags:
        t = srcDt.getSingleAutoTag(tag['id'])
        dstDt.pushAutoTag(t)


def main():
    '''main'''
    srcDt, dstDt = init()
    uploadNewTags(srcDt, dstDt)
    srcAutoTags = srcDt.getAutoTags()
    dstAutoTags = dstDt.getAutoTags()

    # update -> remove  dst tags and push new ones
    # for t in dstAutoTags:
    #    for n in commonTags:
    #        if t['name'] == n:
    #            # delete tag so that it can be pushed again
    #            logging.info('Deleting {}'.format(n))


# >>> exampleSet = [{'type':'type1'},{'type':'type2'},{'type':'type2'}, {'type':'type3'}]
# >>> keyValList = ['type2','type3']
# >>> expectedResult = [d for d in exampleSet if d['type'] in keyValList]


if __name__ == '__main__':
    main()
