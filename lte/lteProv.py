import requests
import const
from log import Logger
import xml.etree.ElementTree as ET

logger = Logger.getLogger('lte', 'logs/lte')

url = "http://c12jb.intranet.slt.com.lk:8080/ClarityServiceManagement-war/ServiceManagementAPIService?wsdl"

headers = {
    'Content-Type': 'text/xml;charset=UTF-8'
}

class Lteprov:
    def lteProv(data, ref):
        logger.info("LTE : %s" % ref + " - " + str(data))

        if data['msisdn'] is not None:                                        
            retmsgsocreate = CreateSO.Create_SO (data,ref) 
            logger.info(ref + ": " + "retmsgsocreate: %s" % retmsgsocreate)
            return {'result': 'success','dataOcs': 'Mconnect_so_create ' + str(retmsgsocreate)}                                                                         
        else:
            return {'result': 'error','dataOcs': 'TaxPrice null against productId','dataPcrf' : 'PCRF error provisioned'}                               
        #resmsg= {"status": "success","description": "Connection success"}
        #return resmsg
        
class CreateSO:

    def Get_SO_details(self,ref):
        data = self
        logger.info("Request : %s" % ref + " - " + str(data))
                    
        # Create the root element
        root = ET.Element(
            'soapenv:Envelope',
            attrib={
                'xmlns:soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                'xmlns:ser': 'http://webservices/clarity/api/servicemanagement'
            }
        )
        header = ET.SubElement(root, 'soapenv:Header')
        body = ET.SubElement(root, 'soapenv:Body')
        service_order = ET.SubElement(body, 'ser:getServiceOrder')
        
        ET.SubElement(service_order, 'ServiceOrderId').text = 'KX202306200006574'      
        
        tree = ET.ElementTree(root)

        xml_string = ET.tostring(root, encoding='utf-8', method='xml')

        print(xml_string.decode('utf-8'))            
        
        body = xml_string.decode('utf-8') 
        logger.info("body : %s" % ref + " - " + body)
        print("body " + body)
        
        try:
            '''response = requests.request("POST", url, headers=headers,data=body.format(bbcircuitid=data['msisdn'], package=data['package'], imsi=data['imsi'],
                                                             customercontact=data['mobile'], mconnectref=data['productSeq']))
            '''
            
            response = requests.request("POST", url, headers=headers,data=body)

            resmsg = response.text
            logger.info("Response User : %s" % ref + " - " + response.text)

            root = ET.fromstring(response.content)
            
            
            return_status = root.find(".//returnStatus")
            
            ws_service_order = root.find(".//wsServiceOrder")

            # Extract values from <returnStatus> element
            if return_status is not None:
                code = return_status.find("code").text
                code_type = return_status.find("codeType").text
                details = return_status.find("details").text
                message = return_status.find("message").text

                print("Return Status:")
                print(f"Code: {code}")
                print(f"Code Type: {code_type}")
                print(f"Details: {details}")
                print(f"Message: {message}")

            # Extract values from <wsServiceOrder> element
            if ws_service_order is not None:
                account_id = ws_service_order.find("accountId").text
                area_code = ws_service_order.find("areaCode").text

                # Continue extracting other elements and values as needed

                print("\nService Order Details:")
                print(f"Account ID: {account_id}")
                print(f"Area Code: {area_code}")

                # Extract and print attributes
                attributes = ws_service_order.findall(".//attributes")
                if attributes:
                    print("\nAttributes:")
                    for attribute in attributes:
                        name = attribute.find("name").text
                        value = attribute.find("value").text
                        print(f"{name}: {value}")

                # Extract and print features
                features = ws_service_order.findall(".//features")
                if features:
                    print("\nFeatures:")
                    for feature in features:
                        feature_name = feature.find("featureName").text
                        print(f"Feature Name: {feature_name}")

                        # Extract and print feature-specific attributes
                        feature_attributes = feature.findall(".//attributes")
                        if feature_attributes:
                            for attr in feature_attributes:
                                attr_name = attr.find("name").text
                                attr_value = attr.find("value").text
                                print(f"  {attr_name}: {attr_value}")
            
            
            
            
            for child in root.iter('code'):
                code = child.text
                print("code " + code)
            
            for child in root.iter('details'):
                details = child.text
                print("details " + details)
                        
            for child in root.iter('serviceOrderId'):
                serviceOrderId = child.text
                print("serviceOrderId " + serviceOrderId)
            
            return serviceOrderId 
        
        except Exception as e: 
            print("Exception : %s" % e)
            logger.info("Exception : %s" % e) 
            return e 
            
    def Create_SO(self,ref):
    
        data = self
        logger.info("Request : %s" % ref + " - " + str(data))
        #xmlfile = open('lte/files/createso.xml', 'r')
                    
        # Create the root element
        root = ET.Element(
            'soapenv:Envelope',
            attrib={
                'xmlns:soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                'xmlns:ser': 'http://webservices/clarity/api/servicemanagement'
            }
        )
        header = ET.SubElement(root, 'soapenv:Header')
        # Create sub-elements within the XML structure
        body = ET.SubElement(root, 'soapenv:Body')
        create_service_order = ET.SubElement(body, 'ser:createServiceOrder')

        service_order = ET.SubElement(create_service_order, 'ServiceOrder')
        ET.SubElement(service_order, 'accountId').text = '0017027379'
        ET.SubElement(service_order, 'addressIdb').text = '12574847'
        ET.SubElement(service_order, 'areaCode').text = 'CEN'

        # Add attributes element
        attributes = ET.SubElement(service_order, 'attributes')
        ET.SubElement(attributes, 'name').text = 'ADSL_CIRCUIT_ID'
        ET.SubElement(attributes, 'value').text = data['msisdn']

        # Add attributes element
        attributes = ET.SubElement(service_order, 'attributes')
        ET.SubElement(attributes, 'name').text = 'BB CIRCUIT ID'
        ET.SubElement(attributes, 'value').text = data['msisdn']

        # Add attributes element
        attributes = ET.SubElement(service_order, 'attributes')
        ET.SubElement(attributes, 'name').text = 'SA_PACKAGE_NAME'
        ET.SubElement(attributes, 'value').text = data['package']

        # Add attributes element
        attributes = ET.SubElement(service_order, 'attributes')
        ET.SubElement(attributes, 'name').text = 'IMSI NO'
        ET.SubElement(attributes, 'value').text = data['imsi']

        # Add attributes element
        attributes = ET.SubElement(service_order, 'attributes')
        ET.SubElement(attributes, 'name').text = 'M_CONNECT_REFERENCE'
        ET.SubElement(attributes, 'value').text = data['productSeq']

        # Add attributes element
        attributes = ET.SubElement(service_order, 'attributes')
        ET.SubElement(attributes, 'name').text = 'MSISDN NO'
        ET.SubElement(attributes, 'value').text = data['msisdn']

        # Add attributes element
        attributes = ET.SubElement(service_order, 'attributes')
        ET.SubElement(attributes, 'name').text = 'CUSTOMER CONTACT'
        ET.SubElement(attributes, 'value').text = data['mobile']
        
        # Add attributes element
        attributes = ET.SubElement(service_order, 'attributes')
        ET.SubElement(attributes, 'name').text = 'SERVICE_SPEED'
        ET.SubElement(attributes, 'value').text = 'LTE'
        
        # Add attributes element
        attributes = ET.SubElement(service_order, 'attributes')
        ET.SubElement(attributes, 'name').text = 'EXCHANGE_AREA_CODE'
        ET.SubElement(attributes, 'value').text = 'CEN'
        
        ET.SubElement(service_order, 'customerId').text = 'CR001695104'
        ET.SubElement(service_order, 'externalId').text = '6ZA43244_4U4R71'
        ET.SubElement(service_order, 'finishDate').text = '2023-08-28T06:01:39.506Z'
        ET.SubElement(service_order, 'orderType').text = 'CREATE-MCONNECT'
        
        ET.SubElement(service_order, 'servicePriority').text = '1'
        ET.SubElement(service_order, 'serviceSpeed').text = 'LTE'
        ET.SubElement(service_order, 'serviceType').text = 'BB-INTERNET'
        ET.SubElement(service_order, 'slaClass').text = 'STANDARD'        
        ET.SubElement(service_order, 'workGroup').text = 'KY-RTOFFICE'        

        # Add more elements as needed

        # Create an ElementTree object
        tree = ET.ElementTree(root)

        # Serialize to a string
        xml_string = ET.tostring(root, encoding='utf-8', method='xml')

        # Print or save the XML
        print(xml_string.decode('utf-8'))            
        
        body = xml_string.decode('utf-8') 
        logger.info("body : %s" % ref + " - " + body)
        print("body " + body)
        
        try:
            '''response = requests.request("POST", url, headers=headers,data=body.format(bbcircuitid=data['msisdn'], package=data['package'], imsi=data['imsi'],
                                                             customercontact=data['mobile'], mconnectref=data['productSeq']))
            '''
            
            response = requests.request("POST", url, headers=headers,data=body)
            
            # prints the response
            resmsg = response.text
            logger.info("Response User : %s" % ref + " - " + response.text)

            root = ET.fromstring(response.content)
            
            for child in root.iter('code'):
                code = child.text
                print("code " + code)
            
            for child in root.iter('details'):
                details = child.text
                print("details " + details)
                        
            for child in root.iter('serviceOrderId'):
                serviceOrderId = child.text
                print("serviceOrderId " + serviceOrderId)
            
            return serviceOrderId 
        
        except Exception as e: 
            print("Exception : %s" % e)
            logger.info("Exception : %s" % e) 
            return e            
