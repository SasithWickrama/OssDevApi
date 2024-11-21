import random
import traceback
import json
from log import Logger
import requests
import db
import json
from datetime import datetime
#import cx_Oracle

logger = Logger.getLogger('entPtlgetFaultdetails', 'logs/entPtlgetFaultdetails')

#Get Fault details 
#=======================            
class Getfaultdetails:
    def dbClarity(self, ref):
        try:
            conn = db.DbConnection.dbconnClaritynew("")  
            logger.info("DB conn : %s" % ref + " - " + str(conn))
            logger.info("@2") 
            if self is not None:
                parmList = [self]
                logger.info("@3")    
                sql = 'SELECT WORO_AREA_CODE,WORO_PROM_NUMBER,WORO_ID,WORO_WORG_NAME,WORO_CREATEDBY,WORO_STAS_ABBREVIATION,WORO_DESCRIPTION,WORO_DATECREATED,WORO_STATUSDATE,WORO_ACTUAL_START_DATE,WORO_ACTUAL_END_DATE FROM WORK_ORDER,CIRCUITS WHERE WORO_PROM_NUMBER  = : 0 AND CIRT_NAME = WORO_CIRT_NAME' 
                logger.info("@4")  
                c = conn.cursor()
                c.execute(sql, parmList)
                results = c.fetchall()
                row_count = len(results)
                result = {}
                data = []
                if row_count == 0:
                    result['data'] = 'No data found'
                    return 'No data found' 
                else:
                    for row in results:
                        data.append({
                            "AREA_CODE": row[0],
                            "PROM_NUMBER": row[1],
                            "WORO_ID": row[2],
                            "WORG_NAME": row[3],
                            "WORO_CREATED_BY": row[4],
                            "WORO_STATUS": row[5],
                            "WORO_DESCRIPTION": row[6],                            
                            "WORO_DATE_CREATED": row[7].isoformat() if row[7] else None,
                            "WORO_DATE_COMPLETED": row[8].isoformat() if row[8] else None,
                            "WORO_ACTUAL_START_DATE": row[9].isoformat() if row[9] else None,
                            "WORO_ACTUAL_END_DATE": row[10].isoformat() if row[10] else None,
                        })  
                    result['data'] = data
                    logger.info("DB Output " + ref + " - " + str(data[0])) 
                    return result
        except Exception as e:
            logger.info("Exception : %s" % ref + " - " + str(e))
            result = "Exception : " + str(e)
            return 'Exception : ' + str(e)
