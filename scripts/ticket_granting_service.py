
"""
This file provides a helper for The ticket granting service.
Needed Information to be able to function:
    - 
    -
Expected functionalities:
    - 
"""
from db_helper import DBHelper
import requests
import time
import string
import json
import random
import base64
from datetime import datetime
import ast
from Crypto.Cipher import AES
from EncryptionHelper import EncryptionHelper


class TicketGrantingService:
    def __init__(self,master_key):
        self.db = DBHelper()
        self.master_key = master_key
        self.eh = EncryptionHelper("TicketGrantingService")

    def duplicate_string(self,input_string):
        while len(input_string) < 16:
            input_string += input_string
        return input_string[:16]

    def process(self, authenticator, tgt, tgr):
        # clean the recevied raw data to process it further
        json_format = tgr.replace("'", "\"")
        tgr = json.loads(json_format)

        # Check if the service requested by the user is present in the KDC database
        status, fetched_service = self.db.fetch_service(str(tgr.get('service_name')))
        if status == -1 : 
            return -1, fetched_service
        service_secret_key = fetched_service.get_secret_key()
        if service_secret_key:
            """
            TGS need to decrypt the ticket granting ticket offered to the client by
            Authentication Server. Note, since this ticket can only be decrypted by
            TGS's secret key, not even the client can know what is inside this. So
            we need to fetch this key from the kdc database.
            """
            status, fetched_tgs = self.db.fetch_service("tgs")
            tgs_secret_key = fetched_tgs.get_secret_key()
            if tgs_secret_key:
                ticket_granting_ticket_plain = self.eh.decrypt(tgt, tgs_secret_key, self.master_key)

                print("Received TGT from Client obtained from Authentication Server")
            else:
                print("Tgs secret key or service not found")


            """
            TGS also need to decrypt the authenticator message from the client node.
            Remember, this message was encrypted using the TGS_SESSION_KEY obtained by the
            client from the Authentication Server. This TGS knows the TGS_SESSION_KEY from
            the above decryption. Now we can make use of the same to decrypt this message.
            """
            authenticator_plain = self.eh.decrypt(authenticator, ticket_granting_ticket_plain.get('tgs_session_key'), self.master_key)

            # compare the username from authenticator as well as tgt
            if authenticator_plain.get('username') == ticket_granting_ticket_plain.get('username'):
                auth_timestamp = datetime.strptime(authenticator_plain.get('timestamp'), "%Y-%m-%d %H:%M:%S.%f")
                tgt_timestamp = datetime.strptime(ticket_granting_ticket_plain.get('timestamp'), "%Y-%m-%d %H:%M:%S.%f")
                elapsed_time_in_hours = divmod((auth_timestamp - tgt_timestamp).seconds, 3600)[0]

                # compare the difference between timestamp authenticator - tgt (threshold is 2 minutes)
                if True:
                    # check if tgt is expired using the lifetime value of the ticket
                    # difference of current timestamp - tgt timestamp < lifetime of ticket
                    # check if it is already cached, if not cache it to avoid replay attacks
                    # generate service session key
                    service_session_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])[0:16]

                    # prepare the service payload for client
                    service_payload = {"username": str(authenticator_plain.get('username')), 
                                       "service_id": str(tgr.get('server_id')),
                                       "timestamp": str(datetime.now()), "lifetime_of_ticket": "2", 
                                       "service_session_key": str(service_session_key)}

                    # encrypt the service payload using service_secret_key
                    service_ticket_encrypted = self.eh.encrypt(service_payload, service_secret_key, self.master_key)

                    # prepare the tgs payload for client
                    tgs_ack_payload = {"service_id": str(tgr.get('service_id')), 
                                       "timestamp": str(datetime.now()), "lifetime_of_ticket": "2", 
                                       "service_session_key": str(service_session_key)}
                    # encrypt the tgs payload using tgs session key
                    tgs_ack_encrypted = self.eh.encrypt(tgs_ack_payload, ticket_granting_ticket_plain.get('tgs_session_key'), self.master_key)
                    # close the open database cursor and connection
                    self.db.close()

                    print("TGS Ack and Service Ticket sent to client")
                    return 1, {"tgs_ack_ticket": tgs_ack_encrypted, 
                                    "service_ticket": service_ticket_encrypted}
            else:
                return -2 , "Access Denied"
