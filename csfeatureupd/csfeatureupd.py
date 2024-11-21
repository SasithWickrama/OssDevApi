import random
import traceback
import json
from log import Logger
import requests
import db
#import cx_Oracle

logger = Logger.getLogger('CSfeatureupd', 'logs/CSfeatureupd')

class CSfeatureupd:
    def dbconnClaritynew(self,ref):
        try:
            conn = db.DbConnection.dbconnClaritynew("")  
            logger.info("DB conn : %s" % ref + " - " + str(conn))

            with conn.cursor() as cursor:                      
                logger.info("Cursor conn : %s" % ref + " @1 " + str(cursor))
                revenue = cursor.callfunc('SLT_CUST_FEATURE_UPD_API',str,[self['BBcircuitNo'], self['operationType']])  
                conn.commit() 
                logger.info("Revenue : %s" % ref + " @2 " + revenue)
            return {'result':'success','resultDesc':'EAZYSTORAGE Feature Updated Success : ' + revenue + " - " +str(self)}
        except Exception as e: 
            logger.info("Exception : %s" % ref + " - " + str(e))
            #return "Exception : %s" % ref + " - " + str(e) + " - " +str(self)
            return {'result':'error','resultDesc': "Exception : %s" % ref + " - " + str(e) + " - " +str(self)}
        