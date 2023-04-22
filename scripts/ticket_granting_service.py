
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
import json
import base64
from datetime import datetime
import ast
from Crypto.Cipher import AES


class TicketGrantingService:
    def __init__(self,master_key):
        self.db = DBHelper()
        self.master_key = master_key

    def duplicate_string(self,input_string):
        while len(input_string) < 16:
            input_string += input_string
        return input_string[:16]

    def process(self, authenticator, tgt, tgr):
        # clean the recevied raw data to process it further
        json_format = tgr.replace("'", "\"")
        tgr = json.loads(json_format)

        # Check if the service requested by the user is present in the KDC database
        fetched_service = self.db.fetch_service(tgr.get('service_name'))
        service_secret_key = fetched_service.get_secret_key()
        if service_secret_key:
            """
            TGS need to decrypt the ticket granting ticket offered to the client by
            Authentication Server. Note, since this ticket can only be decrypted by
            TGS's secret key, not even the client can know what is inside this. So
            we need to fetch this key from the kdc database.
            """
            fetched_tgs = self.db.fetch_service("tgs")
            tgs_secret_key = fetched_tgs.get_secret_key()
            if tgs_secret_key:
                tgs_dec_suite = AES.new(self.duplicate_string(tgs_secret_key).encode('utf8'), AES.MODE_CFB, self.duplicate_string(self.master_key).encode('utf8'))
                print(str(tgt.encode('utf8')))
                ticket_granting_ticket_plain = tgs_dec_suite.decrypt(tgt)
                ticket_granting_ticket_plain = json.loads(str(ticket_granting_ticket_plain)[1:])
                ticket_granting_ticket = ast.literal_eval(ticket_granting_ticket_plain)

                print("Received TGT from Client obtained from Authentication Server")
                print(ticket_granting_ticket)
            else:
                print("Tgs secret key or service not found")


            """
            TGS also need to decrypt the authenticator message from the client node.
            Remember, this message was encrypted using the TGS_SESSION_KEY obtained by the
            client from the Authentication Server. This TGS knows the TGS_SESSION_KEY from
            the above decryption. Now we can make use of the same to decrypt this message.
            """
            auth_dec_suite = AES.new(self.duplicate_string(ticket_granting_ticket.get('tgs_session_key')).encode('utf8'), AES.MODE_CFB, self.duplicate_string(self.master_key).encode('utf8'))
            authenticator_plain = auth_dec_suite.decrypt(authenticator)

            # converting the data from string to python dictionary
            json_format = authenticator_plain.replace("'", "\"")
            authenticator_dict = json.loads(json_format)

            # compare the user_id from authenticator as well as tgt
            if authenticator_dict.get('user_id') == ticket_granting_ticket.get('user_id'):
                auth_timestamp = datetime.strptime(authenticator_dict.get('timestamp'), "%Y-%m-%d %H:%M:%S.%f")
                tgt_timestamp = datetime.strptime(ticket_granting_ticket.get('timestamp'), "%Y-%m-%d %H:%M:%S.%f")
                elapsed_time_in_hours = divmod((auth_timestamp - tgt_timestamp).seconds, 3600)[0]

                # compare the difference between timestamp authenticator - tgt (threshold is 2 minutes)
                if True:
                    # check if tgt is expired using the lifetime value of the ticket
                    # difference of current timestamp - tgt timestamp < lifetime of ticket
                    # check if it is already cached, if not cache it to avoid replay attacks
                    # generate service session key
                    service_session_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])[0:16]

                    # prepare the service payload for client
                    service_payload = {"user_id": str(authenticator_dict.get('user_id')), 
                                       "service_id": str(tgr.get('server_id')),
                                       "timestamp": str(datetime.now()), "lifetime_of_ticket": "2", 
                                       "service_session_key": str(service_session_key)}

                    # encrypt the service payload using service_secret_key
                    service_enc_suite = AES.new(self.duplicate_string(service_secret_key).encode('utf8'), AES.MODE_CFB, self.duplicate_string(self.masterkey).encode('utf8') )
                    service_ticket_encrypted = service_enc_suite.encrypt(str(service_payload))

                    # prepare the tgs payload for client
                    tgs_ack_payload = {"service_id": str(tgr.get('service_id')), 
                                       "timestamp": str(datetime.now()), "lifetime_of_ticket": "2", 
                                       "service_session_key": str(service_session_key)}

                    # encrypt the tgs payload using tgs session key
                    tgs_enc_suite = AES.new(ticket_granting_ticket.get('tgs_session_key'), AES.MODE_CFB, master_key)
                    tgs_ack_encrypted = tgs_enc_suite.encrypt(str(tgs_ack_payload))

                    # close the open database cursor and connection
                    self.db.close()

                    print("TGS Ack and Service Ticket sent to client")
                    return 1, {"tgs_ack_ticket": str(base64.b64encode(tgs_ack_encrypted)), 
                                    "service_ticket": str(base64.b64encode(service_ticket_encrypted))}
            else:
                return -1 , "Access Denied"
