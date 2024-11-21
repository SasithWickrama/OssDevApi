import json
import requests

import const
from log import Logger

logger = Logger.getLogger('pcrf', 'logs/pcrf')


def pcrfToken(data):
    headers = {'subscriberid': data}
    try:
        response = requests.get(
            const.PCRF_TOKEN_URL, headers=headers)

        resmsg = json.loads(response.text)

        # if resmsg['subscriberToken'] is not None:
        if response.status_code == 200:
            responsedata = {"result": "success", "token": resmsg['subscriberToken']}
        else:
            responsedata = {"result": "error", "msg": resmsg['message']}
    except Exception as e:
        responsedata = {"result": "error", "msg": e}

    return responsedata


def pcrfVasData(data):
    headers = {'subscriberid': data}
    try:
        response = requests.get(
            const.PCRF_ADDON_VASDATA_URL, headers=headers)

        resmsg = json.loads(response.text)

        # if resmsg['subscriberToken'] is not None:
        if response.status_code == 200:
            responsedata = {"result": "success", "usage": resmsg['usageDetails']}
        else:
            responsedata = {"result": "error", "msg": resmsg['message']}
    except Exception as e:
        responsedata = {"result": "error", "msg": e}

    return responsedata


def getPackage(pkg_id):
    with open('pcrf/mapping.json') as f:
        data = json.load(f)
        for pkg in data['packages_list']:
            if pkg['offeringID'] == str(pkg_id):
                return pkg['pcrfID']

def getDeletePackage(accountType):
    with open('pcrf/mapping.json') as f:
        data = json.load(f)
        for pkg in data['packages_list']:
            if pkg['accountType'] == str(accountType):
                return pkg['pcrfName']

class Pcrf:

    def pcrfAddonCreate(data, ref, ):

        try:
            logger.info("Token Request : %s" % ref + " - " + str(data))
            result = pcrfToken('94'+data['orderObjectKey'][1:10])
            logger.info("Token Response : %s" % ref + " - " + str(result))

        except Exception as e:
            responsedata = {"result": "error", "msg": "Connection Issue"}
            logger.error("Return : %s" % ref + " - " + str(responsedata))
            return responsedata


        try:
            getpkg = getPackage(data['offeringID'])

            headers = {'subscriberid': result['token'],
                       'Content-Type': 'application/json'}

            payload = {"packageId": getpkg, "commitUser": "OCS", "channel": "OCS"}
            response = requests.post(
                const.PCRF_ADDON_CREATE_URL, headers=headers, data=json.dumps(payload))
            logger.info("Request : %s" % ref + " - " + str(payload))

            resmsg = json.loads(response.text)
            logger.info("Response : %s" % ref + " - " + str(resmsg))

            # if resmsg['status'] == 'SUCCESS':
            if response.status_code == 200:
                responsedata = {"result": "success", "description": resmsg['message'], 'data': data}
                logger.info("Return : %s" % ref + " - " + str(responsedata))
            else:
                responsedata = {"result": "error", "description": resmsg['message'], 'data': data}
                logger.info("Return : %s" % ref + " - " + str(responsedata))

        except Exception as e:
            responsedata = {"result": "error", "description": str(e), 'data': data}
            logger.info("Return : %s" % ref + " - " + str(responsedata))

        return responsedata
