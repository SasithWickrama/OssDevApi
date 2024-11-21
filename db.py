import cx_Oracle


class DbConnection:

    def dbconnHadwh(self):
        try:
            hostname = 'prxd1-scan.intranet.slt.com.lk'
            port = '1521'
            service = 'HADWH'
            user = 'OSS_FAULTS'
            password = 'slt#ossfaults'
            dsn_tns = cx_Oracle.makedsn(hostname, port, service_name=service)
            conn = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
            return {"status": conn}
        except Exception as e:
            print("Exception : %s" % e)
            return {"status": "error","errors": "DB Connection Error "}

    def dbconnClarity(self):
        try:
            hostname = '172.25.1.172'
            port = '1521'
            service = 'clty'
            user = 'OSSPRG'
            password = 'prgoss456'
            dsn_tns = cx_Oracle.makedsn(hostname, port, service_name=service)
            conn = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
            return {"status": conn}
        except Exception as e:
            print("Exception : %s" % e)
            return {"status": "error","errors": "DB Connection Error "}
            
    def dbconnHadwhnew(self):
        try:
            hostname = 'prxd1-scan.intranet.slt.com.lk'
            port = '1521'
            service = 'HADWH'
            user = 'OSS_FAULTS'
            password = 'slt#ossfaults'

            dsn_tns = cx_Oracle.makedsn(hostname, port, service_name=service)
            conn = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
            return conn
        except Exception as e:
            print("Exception : %s" % e)
            return e        
            
            
    def dbconnClaritynew(self):
        try:
            hostname = '172.25.1.172'
            port = '1521'
            service = 'clty'
            user = 'CLTY_API'
            password = 'sncr123'
            dsn_tns = cx_Oracle.makedsn(hostname, port, service_name=service)
            conn = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
            return conn
        except Exception as e:
            print("Exception : %s" % e)
            return e        