"""

 Authentication Server
    - receives:
      - plaintext request for ticket granting ticket (username, name_of_service_requesting, nw_address, lifetime_of_tgt)
    - process:
      - checks whether the given username is in the kdc database (no credential check, only username lookup)
      - if success:
        - generates a random key called SESSION KEY for use between client and TGS.
    - sends:
        - Ticket_Granting_Ticket = ENC(TGS_SECRET_KEY, (username, name_of_service_requested, timestamp, nw_address, lifetime_of_tgt, TGS_SESSION_KEY))
        - Authentication_ACK = ENC(CLIENT_SECRET_KEY, (name_of_service_requested, timestamp, lifetime_of_tgt, TGS_SESSION_KEY))
        - [Authentication_ACK_ENCRYPTED, Ticket_Granting_Ticket_ENCRYPTED]
"""
from db_helper import DBHelper
import random
import string
import base64
from datetime import datetime
from Crypto.Cipher import AES
class AuthenticationServer:
    def __init__(self, masterkey):
        self.db = DBHelper()
        self.masterkey = masterkey
    def duplicate_string(self,input_string):
        while len(input_string) < 16:
            input_string += input_string
        return input_string[:16]
    def login(self,username,password, service, lifetime_of_tgt=10000000):
        status, response = self.db.fetch_user(username)
        if status == 1:
            if response.get_password() == password:
                # Successful
                name, tgs_secret_key = self.db.fetch_service("tgs")
                user_tgs_session_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])[0:16]
                auth_ack_payload = {"service_id": str(service), "timestamp": str(datetime.now()), 
                "lifetime": str(lifetime_of_tgt), "tgs_session_key": str(user_tgs_session_key)}

                tgt_payload = {"user_id": str(username), "service_id": str(service), "timestamp": str(datetime.now()), 
               "lifetime": str(lifetime_of_tgt), "tgs_session_key": str(user_tgs_session_key)}

                ticket_granting_ticket_encryption_suite = AES.new(self.duplicate_string(tgs_secret_key).encode('utf8'), AES.MODE_CFB, self.duplicate_string(self.masterkey).encode('utf8'))
                ticket_granting_ticket = ticket_granting_ticket_encryption_suite.encrypt(str(tgt_payload).encode('utf8'))
                auth_encryption_suite = AES.new(self.duplicate_string(password).encode('utf8'), AES.MODE_CFB, self.duplicate_string(self.masterkey).encode('utf8'))
                auth_ack = auth_encryption_suite.encrypt(str(auth_ack_payload).encode('utf8'))
                print({"ack": base64.b64encode(auth_ack), "tgt": base64.b64encode(ticket_granting_ticket)})
                return {"ack": base64.b64encode(auth_ack), "tgt": base64.b64encode(ticket_granting_ticket)}
            else: 
                print("UNAUTHORIZED")
        else : 
            print(response)
