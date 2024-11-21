import const
from log import Logger
import json
import requests
import db

logger = Logger.getLogger('youTubeUnlimited', 'logs/youTubeUnlimited')

class Ytulprov:
    
    def ytulProv(data, ref):
        logger.info("LTE : %s" % ref + " - " + str(data))
        
        rtnmsg = Ytulprov.pcrfAddonCreate(data, ref)
        if rtnmsg['result'] == 'success':
            return {'result': 'success','resultDesc': 'PCRF and Intermediate table update successful: ' + rtnmsg['resultDesc'] }
        else:
            return {'result': 'Error','resultDesc': 'PCRF and Intermediate table update not successful: ' + rtnmsg['resultDesc'] }
        
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

    def getPackage(pkg_id):
        with open('pcrf/mapping.json') as f:
            data = json.load(f)
            for pkg in data['packages_list']:
                if pkg['offeringID'] == str(pkg_id):
                    return pkg['pcrfID']

    def pcrfAddonCreate(data, ref, ):

        try:
            logger.info("Token Request : %s" % ref + " - " + str(data))
            #result = Ytulprov.pcrfToken('94'+data['msisdnNo'][-9:])
            result = Ytulprov.pcrfToken(data['msisdnNo'])
            logger.info("Token Response : %s" % ref + " - " + str(result))  
                
            if result['result'] == 'success':
                #responsedata = {"result": "success", "description": result['msg']}
                logger.info("Return : %s" % ref + " - " + result['result'])
                    
                try:
                    #getpkg = Ytulprov.getPackage(data['productId'])
                    getpkg = getdetail.dbconnHadwh(data['msisdnNo'],ref)
                    logger.info("Response : %s" % ref + " - " + str(getpkg))
                    if getpkg == 'No data found':
                        return {'result': 'Error','resultDesc': 'Intermediate table return null value for this BB circuit'}
                    else:
                                                
                        if result['result'] == 'success':
                            headers = {'subscriberid': result['token'],
                                        'Content-Type': 'application/json'}
                                        
                            if getpkg['YT_YOUTUBE_PACKAGE'] == '1':
                                pkgid = 59                            
                            elif getpkg['YT_YOUTUBE_PACKAGE'] == '2':
                                pkgid = 60
                            elif getpkg['YT_YOUTUBE_PACKAGE'] == '3':
                                pkgid = 61                            

                            payload = {"packageId": pkgid, "commitUser": "OCS", "channel": "OCS"}
                            response = requests.post(
                                const.PCRF_ADDON_CREATE_URL, headers=headers, data=json.dumps(payload))
                            logger.info("Request : %s" % ref + " - " + str(payload))

                            resmsg = json.loads(response.text)
                            logger.info("Response : %s" % ref + " - " + str(resmsg))
                                
                            # if resmsg['status'] == 'SUCCESS':
                            if response.status_code == 200:
                                responsedata = {"result": "success", "description": resmsg['message']}
                                logger.info("Return ADDON Create: %s" % ref + " - " + str(responsedata))
                                updateTbl = updateDetail.dbconnHadwh(getpkg['YT_ID'],ref)
                                logger.info("Status Update : %s" % ref + " - " + str(updateTbl))
                                return {'result': 'success','resultDesc': 'PCRF and Intermediate table update successfully: ' + resmsg['message']}
                            else:
                                responsedata = {"result": "error", "description": resmsg['message']}
                                logger.info("Return ADDON Create err : %s" % ref + " - " + str(responsedata))
                                return {'result': 'Error','resultDesc': resmsg['message']}
                        else :
                            responsedata = {"result": "error", "description": result['msg']}

                except Exception as e:
                    responsedata = {"result": "error", "description": str(e)}
                    logger.info("Return Exception 2 : %s" % ref + " - " + str(responsedata))
                    return {'result': 'Error','resultDesc': str(e)}
            else:
                responsedata = {"result": "error", "description": result['msg']}
                logger.info("Return error: %s" % ref + " - " + str(responsedata))
                return {'result': 'Error','resultDesc': result['msg']}
                        
        except Exception as ex:
            responsedata = {"result": "error", "msg": "Connection Issue"}
            logger.error("Return Exception 1 : %s" % ref + " - " + str(responsedata))
            return {'result': 'Error','resultDesc': str(ex)}
            

class getdetail:
    def dbconnHadwh(self,ref):
        #logger.info("@1") 
        try:
            conn = db.DbConnection.dbconnClarity("")
            #logger.info("@2") 
            #logger.info("DB Conn :" + conn['status'])
            #print(conn)     
            if conn['status'] == "error": 
                logger.info("DB Conn Status " + str(conn['status']))                
                return 'No data found'
            else:  
                #logger.info("@3") 
                if self is not None:
                    parmList = [self]
                    #sql = 'SELECT YT_BB_SERVICE_ID,YT_CUSTOMER_CONTACT_NO,YT_OUTSTANDING_AMT,YT_OFFER_CREATED_DATE,YT_OFFER_VALID_DATE,YT_YOUTUBE_PACKAGE,YT_OFFER_STATUS,YT_SMS_NOTIFIED_DATE,YT_REMARK,YT_ID FROM CLARITY_ADMIN.YT_UNLIMITED WHERE YT_BB_CIRCUIT = :0'                    
                    sql = 'SELECT YT_BB_SERVICE_ID,YT_CUSTOMER_CONTACT_NO,YT_OUTSTANDING_AMT,YT_OFFER_CREATED_DATE,YT_OFFER_VALID_DATE,YT_YOUTUBE_PACKAGE,YT_OFFER_STATUS,YT_SMS_NOTIFIED_DATE,YT_REMARK,YT_ID FROM CLARITY_ADMIN.YT_UNLIMITED where YT_ID = (select max(YT_ID) from CLARITY_ADMIN.YT_UNLIMITED where YT_BB_CIRCUIT = :0)'
                    c = conn['status'].cursor()
                    #c.execute(sql,{'value':self})
                    c.execute(sql,parmList)
                    results = c.fetchall()
                    #print("results:", results)
                    # Get the row count
                    row_count = len(results)
                    result = {}
                    data=[]
                    if row_count == 0:
                        result['data'] = 'No data found'
                        logger.info("Query Output " + str(result['data'])) 
                        return 'No data found'
                    else:
                        for row in results:
                            data.append({"YT_BB_SERVICE_ID": row[0],
                                         "YT_CUSTOMER_CONTACT_NO": row[1],
                                         "YT_OUTSTANDING_AMT": row[2],
                                         "YT_OFFER_CREATED_DATE": row[3],
                                         "YT_OFFER_VALID_DATE": row[4],
                                         "YT_YOUTUBE_PACKAGE": row[5],
                                         "YT_OFFER_STATUS": row[6],
                                         "YT_SMS_NOTIFIED_DATE": row[7],
                                         "YT_REMARK": row[8],
                                         "YT_ID" : row[9]})   
                        result['data'] = data
                        #print(data[0])
                        logger.info("DB Output " + str(data[0])) 
                        return data[0]
        except Exception as e:
            #result['data']= {"status": "error","errors": "DB Connection Error " + str(e)}
            logger.info("Exception : %s" % ref + " - " + str(e))
            logger.info("Exception " + str(e) )
            return 'No data found'  

import db  # Assuming db module is imported

class updateDetail:
    def dbconnHadwh(self, ref):
        try:
            # Assuming db.DbConnection.dbconnClaritynew returns a connection object
            conn = db.DbConnection.dbconnClaritynew("")
            logger.info("self value : %s - %s" % (ref, str(self)))

            # Define the SQL query outside the cursor context
            sql = 'UPDATE CLARITY_ADMIN.YT_UNLIMITED SET YT_REMARK = :YT_REMARK WHERE YT_REMARK = :value AND YT_ID = :self'
            
            # Use context manager for the cursor to ensure proper handling of resources
            with conn.cursor() as cursor:
                cursor.execute(sql, {"YT_REMARK": "200", "value": "2", "self": str(self)})  # Replace with actual values
                conn.commit()

            return 'YT_UNLIMITED Table Updated Success' + str(self)

        except Exception as e:
            logger.info("Exception: %s - %s" % (ref, str(e)))
            return 'No data found' + str(self)


'''
class updateDetail:
    def dbconnHadwh(self,ref):
        #logger.info("@1") 
        try:
            conn = db.DbConnection.dbconnClaritynew("")
            #logger.info("DB Conn :" + conn['status'])
            #print(conn)     
            #if conn['status'] == "error":                
                #return 'No data found' +  str(self)
            #else:   
                #if self is not None:
                    #parmList = [self]
                    #sql = 'UPDATE CLARITY_ADMIN.YT_UNLIMITED SET YT_REMARK = :YT_REMARK WHERE YT_REMARK = :YT_REMARK AND YT_ID = :value'                    
                    #c = conn.cursor()
                    #c.execute(sql,['200','2',self])
                    
                    #conn.commit()
                    #c.execute(sql,parmList)
                    #results = c.fetchall()
             
            sql = 'UPDATE CLARITY_ADMIN.YT_UNLIMITED SET YT_REMARK = :YT_REMARK WHERE YT_REMARK = :YT_REMARK AND YT_ID = :value'
            with conn.cursor() as cursor2:
                cursor2.execute(sql, ["200","2",self])
                conn.commit()                
            return 'YT_UNLIMITED Table Updated Success' +  str(self)
             
        except Exception as e:
            #result['data']= {"status": "error","errors": "DB Connection Error " + str(e)}
            logger.info("Exception : %s" % ref + " - " + str(e))
            return 'No data found' +  str(self)
            '''