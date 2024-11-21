import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts

from threading import Thread

from flask import make_response, jsonify

import const
from log import Logger

logger = Logger.getLogger('sms', 'logs/sms')


class Sendsms:
    def sendSms(data, ref):

        tpnodestination =data['tpno']
        msg =data['msg']
        smsuser = data['senduser']

        if smsuser == "OSS":
            source = "SLTMOBITEL"
        elif smsuser == "SISU":
            source = "SisuConnect"
        elif smsuser == "SISUCONNECT":
            source = "SisuConnect"
        elif smsuser == "SLTBILL":
            source = "SLTBILL"
        elif smsuser == "1290":
            source = "1290"
        elif smsuser == "RAFM":
            source = "RAFM"
        elif smsuser == "SLTHR":
            source = "SLTHR"
        elif smsuser == "PEOTV":
            source = "PEOTV"
        elif smsuser == "PEOTVGO":
            source = "PEOTVGO"
        elif smsuser == "SLTVC":
            source = "SLTVC"
        else:
            source = "94113011111"

        logger.info("Sms : %s" % ref + " - " + str(data))

        def handle_sent_sm(pdu):
            sys.stdout.write('sent {}\n'.format(pdu.message_id))

        def handle_deliver_sm(pdu):
            sys.stdout.write('delivered {}\n'.format(pdu.receipted_message_id))

        parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(msg)

        client = smpplib.client.Client(const.hostname, const.port)

        # Print when obtain message_id
        client.set_message_sent_handler(lambda pdu: handle_sent_sm(pdu))
        # Handle delivery receipts (and any MO SMS)
        #client.set_message_received_handler(lambda pdu: handle_deliver_sm(pdu))

        client.connect()
        client.bind_transceiver(system_id=const.system_id, password=const.passwd)

        for part in parts:
            pdu = client.send_message(
                source_addr_ton=smpplib.consts.SMPP_TON_ALNUM,
                source_addr_npi=smpplib.consts.SMPP_NPI_UNK,
                # Make sure it is a byte string, not unicode:
                source_addr=source,

                dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                # Make sure these two params are byte strings, not unicode:
                destination_addr=tpnodestination,
                short_message=part,

                data_coding=encoding_flag,
                esm_class=msg_type_flag,
                registered_delivery=True,
            )
        client.unbind()
        return make_response(jsonify(message="success"), 200)


