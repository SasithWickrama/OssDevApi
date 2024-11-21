import json
import random
from datetime import timedelta
import traceback
import requests
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from pcrf.pcrf import Pcrf
from log import Logger
from cx_Oracle import IntegrityError

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
#from waitress import serve

from auth import Authenticate
from sms.sendSms import Sendsms
from lte.lteProv import Lteprov
from ytul.ytulProv import Ytulprov
from requests.auth import HTTPBasicAuth
import const
import db

from csfeatureupd.csfeatureupd import CSfeatureupd
from entportal.getfaultdetails import Getfaultdetails

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config["JWT_SECRET_KEY"] = const.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
jwt = JWTManager(app)
api = Api(app)

logger = Logger.getLogger('server_requests', 'logs/server_requests')
loggerMob = Logger.getLogger('MobitelLtefaults', 'logs/MobitelLtefaults')


def random_ref(length):
    sample_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'  # define the specific string
    # define the condition for random string
    return ''.join((random.choice(sample_string)) for x in range(length))


@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_data):
    return jsonify({"result": "error", "msg": "Token has expired"}), 401


@jwt.invalid_token_loader
def my_invalid_token_callback(jwt_data):
    return jsonify({"result": "error", "msg": "Invalid Token"}), 401


@jwt.unauthorized_loader
def my_unauthorized_loader_callback(jwt_data):
    return jsonify({"result": "error", "msg": "Missing Authorization Header"}), 401

def getAuthKey(userid):
    with open('auth.json') as f:
        data = json.load(f)
        for usr in data['user_list']:
            if usr['username'] == str(userid):
                return usr['authkey']

# TOKEN GET
class GetToken(Resource):
    def get(self):
        ref = random_ref(15)
        logger.info(ref + " - " + str(request.remote_addr) + " - " + str(request.url) + " - " + str(request.headers))
        data = request.get_json()
        return Authenticate.generateToken(data, ref)
    
# TOKEN POST    
class GetTokenpost(Resource):
    def post(self):
        ref = random_ref(15)
        logger.info(ref + " - " + str(request.remote_addr) + " - " + str(request.url) + " - " + str(request.headers))
        data = request.get_json()
        return Authenticate.generateToken(data, ref)        

# SMS
class SendSms(Resource):
    #@jwt_required()
    def post(self):
        ref = random_ref(15)
        logger.info(ref + " - " + str(request.remote_addr) + " - " + str(request.url) + " - " + str(request.headers))
        data = request.get_json()
        return Sendsms.sendSms(data, ref)

#LTE
class LteProv(Resource):
    #@jwt_required()
    def post(self):
        ref = random_ref(15)
        logger.info(ref + " - " + str(request.remote_addr) + " - " + str(request.url) + " - " + str(request.headers))
        data = request.get_json()
        return Lteprov.lteProv(data,ref)

#MOBITEL OCS get details from HADWH
#=======================
class callMySlt:
    def exeDb(self):
        try:
            conn = db.DbConnection.dbconnHadwh("")
            print(conn)
            if conn['status'] == "error":
                return conn
            else:  
                if self == "Primary Offering" or self == "Main Packages" or self == "Add-ons":
                    sql = 'SELECT * FROM OSS_FAULTS.LTE_OCS_PCRF_DATA WHERE PACKAGE_TYPE = :value'
                    c = conn['status'].cursor()
                    c.execute(sql,{'value':self})
                    result = {}
                    data=[]
                    for row in c:
                        data.append({"PACKAGE_TYPE": row[0],
                                    "ADDON_NAME": row[1],
                                    "MYSLT_PKG_NAME": row[2],
                                    "RECURRENCE": row[3],
                                    "DATA_VOLUME_GB": row[4],
                                    "VALIDITY": row[5],
                                    "PRICE_LKR_WITHOUT_TAX": row[6],
                                    "PRICE_LKR_WITH_TAX": row[7],
                                    "PACKAGE_ID": row[8],
                                    "PCRF_PKG_NAME": row[9],
                                    "OFFERING_NAME": row[10],
                                    "OFFERING_ID": row[11],
                                    "OFFERING_CATEGORY": row[12],
                                    "DATA_ACCOUNT_TYPE": row[13],
                                    "DATA_FREE_UNIT_TYPE": row[14],
                                    "VOICE_ACCOUNT_TYPE": row[15],
                                    "VOICE_FREE_UNIT_TYPE": row[16],
                                    "VOICE_VOLUME": row[17]})   
                    result['data'] = data
                    return result
                else:
                    sql = 'SELECT * FROM OSS_FAULTS.LTE_OCS_PCRF_DATA'
                    c = conn['status'].cursor()
                    c.execute(sql)
                    result = {}
                    data=[]
                    for row in c:
                        data.append({"PACKAGE_TYPE": row[0],
                                    "ADDON_NAME": row[1],
                                    "MYSLT_PKG_NAME": row[2],
                                    "RECURRENCE": row[3],
                                    "DATA_VOLUME_GB": row[4],
                                    "VALIDITY": row[5],
                                    "PRICE_LKR_WITHOUT_TAX": row[6],
                                    "PRICE_LKR_WITH_TAX": row[7],
                                    "PACKAGE_ID": row[8],
                                    "PCRF_PKG_NAME": row[9],
                                    "OFFERING_NAME": row[10],
                                    "OFFERING_ID": row[11],
                                    "OFFERING_CATEGORY": row[12],
                                    "DATA_ACCOUNT_TYPE": row[13],
                                    "DATA_FREE_UNIT_TYPE": row[14],
                                    "VOICE_ACCOUNT_TYPE": row[15],
                                    "VOICE_FREE_UNIT_TYPE": row[16],
                                    "VOICE_VOLUME": row[17]})    
                    result['data'] = data
                    return result
        except Exception as e:
            #result['data']= {"status": "error","errors": "DB Connection Error"}
            #logger.info("Exception : %s" % ref + " - " + str(e))
            return str(e)

class getDetails(Resource):
    #@jwt_required()
    def post(self):         
        data = request.get_json()
        return  callMySlt.exeDb(data['packageType'])

#==================================================

loggerocsApi = Logger.getLogger('OCSOffer', 'logs/OCSOffer') 
loggeroffer = Logger.getLogger('add_del_Offer', 'logs/add_del_Offer')

headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json'}
    #'Authorization': f'Basic 'SLTUSR':'SLTPW''} 
auth = HTTPBasicAuth('SLTUSR', 'SLTPW')  

class offerRecharge(Resource):

    def post(self):

        ref = random_ref(15)
        data = request.get_json()
        loggerocsApi.info(ref + ": " + "data : %s" % data)

        try:

            if data ['msisdnNo'] and data ['productId'] and data ['offerName'] and data ['operationType'] and data ['channelName']:

                data ['channelSeq'] = None

                #Offer Add only OCS provisioning
                if data ['operationType'] == 'ADD_OFFERING' and (data['productId'] != '61000011' and data['productId'] != '61000012'):

                    retmsg = OCSaddOffer.OCS_ADD_Offer (data ['msisdnNo'],data ['productId'],data ['operationType'],data ['channelSeq'])
                    loggerocsApi.info(ref + ": " + "retmsgadd : %s" % retmsg)

                    if retmsg['resultHeader']['resultCode'] == '0':
                        return {'result': 'success','dataOcs': 'ADD_OFFERING: ' + retmsg['resultHeader']['resultDesc'],'dataPcrf' : 'Offer ID is not relevant to PCRF provisioning'}
                    else:
                        return {'result': 'error','dataOcs': 'ADD_OFFERING: ' + retmsg['resultHeader']['resultDesc'],'dataPcrf' : 'Offer ID is not relevant to PCRF provisioning'}

                #Offer Delete only OCS provisioning
                elif data ['operationType'] == 'DEL_OFFERING' and (data['productId'] != '61000011' and data['productId'] != '61000012'):

                    retmsg = OCSaddOffer.OCS_ADD_Offer (data ['msisdnNo'],data ['productId'],data ['operationType'],data ['channelSeq'])
                    loggerocsApi.info(ref + ": " + "retmsgadd : %s" % retmsg)

                    if retmsg['resultHeader']['resultCode'] == '0':
                        return {'result': 'success','dataOcs':  'DEL_OFFERING ' + retmsg['resultHeader']['resultDesc'],'dataPcrf' : 'Offer ID is not relevant to PCRF provisioning'}
                    else:
                        return {'result': 'error','dataOcs': 'DEL_OFFERING ' + retmsg['resultHeader']['resultDesc'],'dataPcrf' : 'Offer ID is not relevant to PCRF provisioning'}

                #Offer Add for both OCS and PCRF provisioning but not success
                elif data ['operationType'] == 'ADD_OFFERING' and (data['productId'] == '61000011' or data['productId'] == '61000012'):

                    retmsg = OCSaddOffer.OCS_ADD_Offer (data ['msisdnNo'],data ['productId'],data ['operationType'],data ['channelSeq'])
                    loggerocsApi.info(ref + ": " + "retmsgadd : %s" % retmsg)

                    if retmsg['resultHeader']['resultCode'] == '0':
                        retmsg_pcrf = Pcrf.pcrfAddonCreate(data, ref)
                        loggerocsApi.info(ref + ": " + "retmsg_pcrf : %s" % retmsg_pcrf)

                    else:
                        return {'result': 'error','dataOcs': 'ADD_OFFERING ' + retmsg['resultHeader']['resultDesc'],'dataPcrf' : 'PCRF platform is not provisioned due to '+ retmsg['resultHeader']['resultDesc']}
                        #return {'result': 'error','dataOcs': 'ADD_OFFERING ' + retmsg['resultHeader']['resultDesc'],'dataPcrf' : 'PCRF platform is not provisioned due to '+ retmsg['resultHeader']['resultDesc']}
                        #return {'result': 'error','dataOcs': 'ADD_OFFERING ','dataPcrf' : 'PCRF platform is not provisioned due to'}

                    if retmsg['resultHeader']['resultCode'] == '0' and retmsg_pcrf['result'] == 'error':

                        if "changeSubOfferingResult" in retmsg:

                            puchseq = retmsg['changeSubOfferingResult']['offering']

                            if "purchasingSeq" in puchseq[0]['offeringKey']:
                                loggerocsApi.info(ref + ": " + "purchasingSeq : %s" % puchseq[0]['offeringKey']['purchasingSeq'])
                                retmsgDel = OCSaddOffer.OCS_ADD_Offer (data ['msisdnNo'],data ['productId'],'DEL_OFFERING',puchseq[0]['offeringKey']['purchasingSeq'])
                                loggerocsApi.info(ref + ": " + "retmsgDeloffer : %s" % retmsgDel)
                                if retmsgDel['resultHeader']['resultCode'] == '0':

                                    retTaxPrice = getPackageprice(data['productId'])

                                    if retTaxPrice is not None:
                                        loggerocsApi.info(ref + ": " + "retmsgTaxPrice : %s" % retTaxPrice)

                                        if retTaxPrice is not None:

                                            retmsgadjustment = OCSadjustment.OCS_adjustment (data ['msisdnNo'],(retTaxPrice),"1")
                                            loggerocsApi.info(ref + ": " + "retmsgAdjustment: %s" % retmsgadjustment)

                                            return {'result': 'error','dataOcs': 'ADJUSTMENT ' + retmsgadjustment['resultHeader']['resultDesc'],'dataPcrf' : 'PCRF error provisioned'}

                                        else:
                                            return {'result': 'error','dataOcs': 'TaxPrice null against productId','dataPcrf' : 'PCRF error provisioned'}
                                    else:
                                        return {'result': 'error','dataOcs': 'TaxPrice null against productId','dataPcrf' : 'PCRF error provisioned'}

                                else:
                                    return {'result': 'error','dataOcs': 'DEL_OFFERING: ' + retmsgDel['resultHeader']['resultDesc'],'dataPcrf' : 'PCRF error provisioned'}
                            else:
                                return {'result': 'error','dataOcs': retmsg['resultHeader']['resultDesc'],'dataPcrf' : retmsg_pcrf['description']}
                        else:
                            return {'result': 'error','dataOcs': retmsg['resultHeader']['resultDesc'],'dataPcrf' : retmsg_pcrf['description']}

                    #Offer Add for both OCS and PCRF Provisioning both Success
                    elif retmsg['resultHeader']['resultCode'] == '0' and retmsg_pcrf['result'] == 'success':
                        return {'result': 'success','dataOcs': retmsg['resultHeader']['resultDesc'],'dataPcrf' : retmsg_pcrf['description']}
                    else:
                        return {'result': 'error','dataOcs': retmsg['resultHeader']['resultDesc'],'dataPcrf' : retmsg_pcrf['description']}

                #Offer Add for both OCS and PCRF Provisioning both Success
                elif data ['operationType'] == 'DEL_OFFERING'and (data['productId'] == '61000011' or data['productId'] == '61000012'):

                    retmsg = OCSaddOffer.OCS_ADD_Offer (data ['msisdnNo'],data ['productId'],data ['operationType'],data ['channelSeq'])
                    loggerocsApi.info(ref + ": " + "retmsgadd : %s" % retmsg)

                    if retmsg['resultHeader']['resultCode'] == '0':
                        retmsg_pcrf = Pcrf.pcrfAddonCreate(data, ref)
                        loggerocsApi.info(ref + ": " + "retmsg_pcrf : %s" % retmsg_pcrf)

                    else:
                        return {'result': 'error','dataOcs': 'DEL_OFFERING ' + retmsg['resultHeader']['resultDesc'],'dataPcrf' : 'PCRF platform is not provisioned due to '+ retmsg['resultHeader']['resultDesc']}

                    if retmsg['resultHeader']['resultCode'] == '0' and retmsg_pcrf['result'] == 'error':

                        if "changeSubOfferingResult" in retmsg:

                            puchseq = retmsg['changeSubOfferingResult']['offering']

                            if "purchasingSeq" in puchseq[0]['offeringKey']:

                                retmsgDel = OCSaddOffer.OCS_ADD_Offer (data ['msisdnNo'],data ['productId'],'ADD_OFFERING',puchseq[0]['offeringKey']['purchasingSeq'])
                                loggerocsApi.info(ref + ": " + "retmsgDeloffer : %s" % retmsgDel)
                                if retmsgDel['resultHeader']['resultCode'] == '0':

                                    retTaxPrice = getPackageprice(data['productId'])

                                    if retTaxPrice is not None:
                                        loggerocsApi.info(ref + ": " + "retmsgTaxPrice : %s" % retTaxPrice)

                                        if retTaxPrice is not None:

                                            retmsgadjustment = OCSadjustment.OCS_adjustment (data ['msisdnNo'],(retTaxPrice),"2")
                                            loggerocsApi.info(ref + ": " + "retmsgAdjustment: %s" % retmsgadjustment)

                                            return {'result': 'error','dataOcs': 'ADJUSTMENT ' + retmsgadjustment['resultHeader']['resultDesc'],'dataPcrf' : 'PCRF error provisioned'}

                                        else:
                                            return {'result': 'error','dataOcs': 'TaxPrice null against productId','dataPcrf' : 'PCRF error provisioned'}
                                    else:
                                        return {'result': 'error','dataOcs': 'TaxPrice null against productId','dataPcrf' : 'PCRF error provisioned'}

                                else:
                                    return {'result': 'error','dataOcs': 'ADD_OFFERING: ' + retmsgDel['resultHeader']['resultDesc'],'dataPcrf' : 'PCRF error provisioned'}
                            else:
                                return {'result': 'error','dataOcs': retmsg['resultHeader']['resultDesc'],'dataPcrf' : retmsg_pcrf['description']}
                        else:
                            return {'result': 'error','dataOcs': retmsg['resultHeader']['resultDesc'],'dataPcrf' : retmsg_pcrf['description']}
                else:
                    return {'result': 'error','dataOcs': retmsg['resultHeader']['resultDesc'],'dataPcrf' : retmsg_pcrf['description']}
            else:
                return {'result': 'error', 'description': 'request json value parameter data missing','data': 'PCRF error'}
                #return {'result': retmsg}
        except Exception as e:
            print(e)
            return {'result': 'error', 'description': 'request json key parameter wrong or missing','data': e}



class OCSaddOffer:

    def OCS_ADD_Offer(self, OfferId ,OfferType ,channelSeq):

        data = {
            "requestHeader": {
                "operationType": OfferType,
                "requestedBy": "slt",
                "systemName": "SLT_OCS_INT"
            },
            "primaryIdentity": self,
            "offeringList": [
                {
                    "offeringId": OfferId,
                    "purchaseSeq": channelSeq
                }
            ]
        }

        loggeroffer.info("Request : %s" % data)
        try:

            response = requests.post('http://10.253.0.211/sltServices/ocs/integration/offering', data=json.dumps(data),
                                     headers=headers,auth=auth)

            loggeroffer.info("Response Code: %s" % response.status_code)
            resmsg = response.json()
            print(resmsg)
            #responsedata = {"data": resmsg['data']}
            loggeroffer.info("Response : %s" % resmsg)
            return resmsg

        except Exception as e:
            #print("Exception : %s" % traceback.format_exc())
            loggeroffer.info("Exception : %s" % e)

class OCSadjustment:

    def OCS_adjustment(self, adjAmount, adjType):

        data = {
            "requestHeader": {
                "operationType": "ADJUST_ACC",
                "requestedBy": "slt",
                "systemName": "SLT_OCS_INT"
            },
            "primaryIdentity": self,
            "adjAmount": adjAmount,
            "adjType": adjType,
            "remark":"Adjusted due to OCS Addon error from MY_SLT app"
        }

        print (data)
        loggeroffer.info("Request : %s" % data)
        try:

            response = requests.post('http://10.253.0.211/sltServices/ocs/integration/adjustment', data=json.dumps(data),
                                     headers=headers,auth=auth)

            loggeroffer.info("Response Code: %s" % response.status_code)
            resmsg = response.json()
            print(resmsg)
            #responsedata = {"data": resmsg['data']}
            loggeroffer.info("Response : %s" % resmsg)
            return resmsg

        except Exception as e:
            print("Exception : %s" % e)
            loggeroffer.info("Exception : %s" % e)

class callCitycode:

    def exeDb(self):
        try:
            conn = db.DbConnection.dbconnHadwh("")
            print(conn)
            if conn['status'] == "error":
                return conn
            else:  
                if self is not None:
                    sql = 'SELECT * FROM OSS_FAULTS.MCONNECT_CITY_RTOM_NEW WHERE CITY = :value'
                    c = conn['status'].cursor()
                    c.execute(sql,{'value':self})
                    result = {}
                    data=[]
                    for row in c:
                        data.append({"RTOM_AREA": row[0],
                                    "CITY": row[1],
                                    "LATITUDE": row[2],
                                    "LONGITUDE": row[3],
                                    "STATUS": row[4],
                                    "DISTRICT": row[5],
                                    "PROVINCE": row[6],
                                    "OVERLAPS": row[7],
                                    "POSTAL_CODE": row[8],
                                    "CITY_CODE": row[9],
                                    "LEA_CODE": row[10],
                                    "COST_CENTER": row[11],
                                    "SLT_BILLING_CENTER_NAME": row[12]})   
                    result['data'] = data
                    return result
                else:
                    result['data'] = "city parameter can not be null"
                    return result
        except Exception as e:
            #result['data']= {"status": "error","errors": "DB Connection Error"}
            #logger.info("Exception : %s" % ref + " - " + str(e))
            return str(e)

class getImsiValidation:

    def exeDb(self):
        try:
            conn = db.DbConnection.dbconnClarity("")
            print(conn)
            if conn['status'] == "error":
                return conn
            else:  
                if self is not None:
                    sql = 'SELECT COUNT(*) FROM OSSPRG.LTEKI_MCONNECT WHERE IMSI = :value'
                    c = conn['status'].cursor()
                    c.execute(sql,{'value':self})
                    result = {}
                    data=[]
                    for row in c:
                        data.append({"IMSI": row[0]})   

                    if data[0]['IMSI'] == 1:
                        result['data'] = "Success"
                        return result
                    if data[0]['IMSI'] == 0:
                        result['data'] = "Error"
                        return result    
                    else:
                        result['data'] = "Multiple SIM in DB"
                        return result
                else:
                    result['data'] = "IMSI parameter can not be null"
                    return result
        except Exception as e:
            #result['data']= {"status": "error","errors": "DB Connection Error"}
            logger.info("Exception : %s" % ref + " - " + str(e))
            return str(e)
            
'''
class setMobFaultstatus:

    def setFaultdetails(self,ref,resdata):
        try:
            loggerMob.info(f"@1 {str(ref)}")
            conn = db.DbConnection.dbconnClarity("")
            loggerMob.info(f"DB Connection: {str(ref)} - {str(conn)}")
            print(conn)
            if conn['status'] == "error":
                return conn
            else:  
                if self is not None:
                    sql = 'SELECT COUNT(*) FROM OSSPRG.MOBITEL_LTE_FAULT_HANDLER WHERE MLF_MOBSR_ID = :value'
                    c = conn['status'].cursor()
                    c.execute(sql,{'value':self})
                    result = {}
                    data=[]
                    for row in c:
                        data.append({"SRNumber": row[0]}) 
                        loggerMob.info(f"SQL results: {str(ref)} - {str(result)}") 

                    if data[0]['SRNumber'] == 1:
                        result['msg'] = "Success"
                        result['result'] = "OSS Fault Cleared and Confirm"
                        loggerMob.info(f"SRNumber: {str(ref)} - {result}")
                        return result
                    if data[0]['SRNumber'] == 0:
                        result['msg'] = "Error"
                        result['result'] = "SRNumber Invalied"
                        loggerMob.info(f"SRNumber: {str(ref)} - {result}")
                        return result    
                    else:
                        result['msg'] = "Error"
                        result['result'] = "Multiple records for SRNumber"
                        return result
                else:
                    result['msg'] = "Error"
                    result['result'] = "SRNumber can not be null"
                    return result
        except Exception as e:
            loggerMob.info(f"Exception: {str(ref)} - {str(e)}")
            return str(e)
'''

class setMobFaultstatus:

    def setFaultdetails(self, ref, resdata):
        try:
            loggerMob.info(f"@1 {str(ref)}")
            conn = db.DbConnection.dbconnClarity("")
            loggerMob.info(f"DB Connection: {str(ref)} - {str(conn)}")
            print(conn)
            if conn['status'] == "error":
                return conn
            else:  
                if self is not None:
                    sql_select = 'SELECT COUNT(*) FROM OSSPRG.MOBITEL_LTE_FAULT_HANDLER WHERE MLF_MOBSR_ID = :value'
                    c = conn['status'].cursor()
                    c.execute(sql_select, {'value': self})
                    result = {}
                    data = []
                    for row in c:
                        data.append({"SRNumber": row[0]}) 
                        loggerMob.info(f"SQL results: {str(ref)} - {str(result)}") 

                    if data[0]['SRNumber'] == 1:
                        sql_insert = '''INSERT INTO OSSPRG.MOBITEL_LTE_UPDATED_FAULTS (
                                           MLUF_ID, MLUP_PROB_NUMBER, MLUP_FAULT_STATUS,
                                           MLUP_RETURN_REMARKS, MLUP_TEST_OBSERVATIONS, MLUP_CAUSE_OF_FAULT,
                                           MLUP_FAULT_IN, MLUP_IMPACT, CLEARED_DATE,
                                           CONFIRM_DATE, MLUP_ADDITIONAL_REMARKS, MLUP_INSERTED_DATE,
                                           MLUP_MLF_MOBITEL_ID, MLUP_MLF_MOBSR_ID, MLUP_STATUS,
                                           MLUP_STATUS_DATE, MLUP_WORK_GROUP)
                                       VALUES (MLUF_ID_SEQ.NEXTVAL,
                                               :prob_number,
                                               :fault_status,
                                               :return_remarks,
                                               :test_observations,
                                               :cause_of_fault,
                                               :fault_in,
                                               :impact,
                                               TO_DATE(:cleared_date, 'YYYY-MM-DD"T"HH24:MI:SS'),
                                               TO_DATE(:confirm_date, 'YYYY-MM-DD"T"HH24:MI:SS'),
                                               :additional_remarks,
                                               SYSDATE,
                                               :id,
                                               :srnumber,
                                               '1',
                                               SYSDATE,
                                               '')'''
                        c.execute(sql_insert, {'prob_number': '',
                                               'fault_status': resdata['FaultStatus'],
                                               'return_remarks': resdata['Return_Remarks'],
                                               'test_observations': resdata['Test_Observations'],
                                               'cause_of_fault': resdata['Cause_of_Fault'],
                                               'fault_in': resdata['Fault_In'],
                                               'impact': resdata['Impact'],
                                               'cleared_date': resdata['ClearedDate'],
                                               'confirm_date': resdata['ConfirmDate'],
                                               'additional_remarks': resdata['Additional_Remarks'],
                                               'id': resdata['Id'],
                                               'srnumber': resdata['SRNumber']})
                        conn['status'].commit()
                        result['msg'] = "Success"
                        result['result'] = "OSS Fault Cleared and Confirm"
                        loggerMob.info(f"SRNumber: {str(ref)} - {result}")
                        return result
                    elif data[0]['SRNumber'] == 0:
                        result['msg'] = "Error"
                        result['result'] = "SRNumber Invalid"
                        loggerMob.info(f"SRNumber: {str(ref)} - {result}")
                        return result    
                    else:
                        result['msg'] = "Error"
                        result['result'] = "Multiple records for SRNumber"
                        return result
                else:
                    result['msg'] = "Error"
                    result['result'] = "SRNumber cannot be null"
                    return result
        #except Exception as e:
            #loggerMob.info(f"Exception: {str(ref)} - {str(e)}")
            #result['msg'] = "Error"
            #result['result'] = (f"OSS Fault Cleared and Confirm : {str(ref)} - {str(e)}")
            #return str(e)
        except IntegrityError as integrity_error:
            if integrity_error.args[0].code == 1:
                # Unique constraint violation occurred
                result['msg'] = "Error"
                result['result'] = "Unique constraint violated. This record already exists."
                loggerMob.error(f"Unique constraint violation: {str(ref)} - {str(integrity_error)}")
                return result
            else:
                # Other integrity constraint violation
                loggerMob.error(f"Integrity constraint violation: {str(ref)} - {str(integrity_error)}")
                return str(integrity_error)
        except Exception as e:
            loggerMob.info(f"Exception: {str(ref)} - {str(e)}")
            result['msg'] = "Error"
            result['result'] = (f"OSS Fault Cleared and Confirm : {str(ref)} - {str(e)}")
            return str(e)

class getsimValid(Resource):
    def post(self):         
        data = request.get_json()
        return  getImsiValidation.exeDb(data['ImsiNo'])
        #print(data)
        #return {'data': result}

class getCitycode(Resource):
    def post(self):         
        data = request.get_json()
        return  callCitycode.exeDb(data['city'])
        #print(data)
        #return {'data': result}

def getPackageprice(pkg_id):
    with open('pcrf/mapping.json') as f:
        data = json.load(f)
        for pkg in data['packages_list']:
            if pkg['offeringID'] == str(pkg_id):
                return pkg['pricewithTax']

#youTube unlimited package (BSS to MY_SLT) 12_06_2023
class youTubeunLimited(Resource):
    #@jwt_required()
    def post(self):
        ref = random_ref(15)
        logger.info(ref + " - " + str(request.remote_addr) + " - " + str(request.url) + " - " + str(request.headers))
        data = request.get_json()
        return Ytulprov.ytulProv(data,ref)

#CS Storage UpdateFeature
class UpdateFeature(Resource):
    #@jwt_required()
    def post(self):
        ref = random_ref(15)
        data = request.get_json()
        return CSfeatureupd.dbconnClaritynew(data,ref)

#Entprise Portal API to get fault details       
class EntgetFault(Resource):
    #@jwt_required()
    def post(self):
        ref = random_ref(15)
        data = request.get_json()
        logger.info(ref + " - " + str(request.remote_addr) + " - " + str(request.url) + " - " + str(request.headers))
        return Getfaultdetails.dbClarity(data['faultId'],ref)

#setFaultStatus for Mobitel LTE Fault dev
class setFaultstatus(Resource):
    @jwt_required()
    def post(self):
        ref = random_ref(15)
        data = request.get_json()
        loggerMob.info("Request Json File: %s" % data)
        return setMobFaultstatus.setFaultdetails(data['SRNumber'],ref,data)

# API URL PATH
# TOKEN POST
api.add_resource(GetTokenpost, const.APP_ROUTE_TOKEN_POST)

# TOKEN GET
api.add_resource(GetToken, const.APP_ROUTE_TOKEN)

# SMS
api.add_resource(SendSms, const.APP_ROUTE_SMS)

#LTE for M-Connect
api.add_resource(LteProv,const.APP_ROUTE_LTE)

#getCityCode for M-Connect
api.add_resource(getCitycode, '/api/mySltOcs/citycode/')

# MODIFY ROUTES
api.add_resource(getDetails, const.APP_ROUTE_MAPPING)

#OFFER
api.add_resource(offerRecharge, const.APP_ROUTE_OFFER)

#youTube unlimited package (BSS to MY_SLT)
api.add_resource(youTubeunLimited, const.APP_YOUTUBE_UL)

#CS Storage
api.add_resource(UpdateFeature, '/api/storage/updatefeature/')

#Entprise Portal APIs
api.add_resource(EntgetFault, '/api/entportal/getfaultdetails/')

#getsimValid for M-Connect
api.add_resource(getsimValid, '/api/mySltOcs/getsimValid/')

#setFaultStatus for Mobitel LTE Fault dev
api.add_resource(setFaultstatus, '/sltmobiltel/LTEFaults/faultstatus/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=22550)
    #serve(app, host='0.0.0.0', port=20001, threads=3)
    #Sasith