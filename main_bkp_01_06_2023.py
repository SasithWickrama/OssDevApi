import json
import random
from datetime import timedelta
import traceback
import requests
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from log import Logger

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
#from waitress import serve

from auth import Authenticate
from sms.sendSms import Sendsms
from lte.lteProv import Lteprov
from requests.auth import HTTPBasicAuth
import const
import db

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config["JWT_SECRET_KEY"] = const.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
jwt = JWTManager(app)
api = Api(app)

logger = Logger.getLogger('server_requests', 'logs/server_requests')


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


# TOKEN
class GetToken(Resource):
    def get(self):
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


#MOBITEL OCS
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
    #@jwt_required()
    def post(self):         
        data = request.get_json()     
        loggerocsApi.info("data : %s" % data)
        try:
            if data ['msisdnNo'] and data ['productId'] and data ['offerName'] and data ['operationType'] and data ['channelName']:
                
                if data ['operationType'] == 'ADD_OFFERING':                    
                    retmsg = OCSaddOffer.OCS_ADD_Offer (data ['msisdnNo'],data ['productId'],data ['operationType'])    
                    loggerocsApi.info("retmsgadd : %s" % retmsg)                       
                  
                elif data ['operationType'] == 'DEL_OFFERING':
                    retmsg = OCSaddOffer.OCS_ADD_Offer (data ['msisdnNo'],data ['productId'],data ['operationType'])
                    loggerocsApi.info("retmsgdel : %s" % retmsg) 
                    
                print(retmsg['resultHeader']['resultCode'])
                loggerocsApi.info("result1 : %s" % retmsg)
                    
                if (retmsg['resultHeader']['resultCode'])== '0':
                    return {'result': 'success','data': retmsg} 
                else:
                    return {'result': 'error','data': retmsg} 
            else:            
                return {'result': 'error', 'description': 'request json value parameter data missing','data': data} 
                #return {'result': retmsg}         
        except Exception as e:
            loggerocsApi.info('Exception: '+ str(e))
            return {'result': 'error', 'description': 'request json key parameter wrong or missing#','data': data} 

class OCSaddOffer:
    
    def OCS_ADD_Offer(self, OfferId ,OfferType):
        
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
                "purchaseSeq": "null"
                }
                ]
                }

        loggeroffer.info("Request : %s" % data)
        try:

            response = requests.post('http://10.253.0.211/sltServices/ocs/integration/offering', data=json.dumps(data),
                                           headers=headers,auth=auth)

            loggeroffer.info("Response Code: %s" % response.status_code)
            resmsg = response.json()
            #responsedata = {"data": resmsg['data']}
            loggeroffer.info("Response : %s" % resmsg)

            return resmsg
        except Exception as e:
            print("Exception : %s" % traceback.format_exc())
            loggeroffer.info("Exception : %s" % traceback.format_exc())


# API URL PATH
# TOKEN
api.add_resource(GetToken, const.APP_ROUTE_TOKEN)

# SMS
api.add_resource(SendSms, const.APP_ROUTE_SMS)

#LTE
api.add_resource(LteProv,const.APP_ROUTE_LTE)

# MODIFY ROUTES
api.add_resource(getDetails, const.APP_ROUTE_MAPPING)

#OFFER
api.add_resource(offerRecharge, const.APP_ROUTE_OFFER)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=22550)
    #serve(app, host='0.0.0.0', port=20001, threads=3)
