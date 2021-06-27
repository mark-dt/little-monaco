import logging
import requests
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