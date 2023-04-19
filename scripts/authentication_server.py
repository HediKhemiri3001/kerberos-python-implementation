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
from Crypto.Cipher import AES
from kdc_main import master_key
class AuthenticationServer:
    def __init__(self):
        self.db = DBHelper()
    def login(self,username,password, service):
        status, response = self.db.fetch_user(username)
        if status == 1:
            if response.get_password() == password:
                # Successful
                serviceStatus, service = self.db.fetch_service("tgs")
                
                user_tgs_session_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(16)])[0:16]

                auth_encryption_suite = AES.new(password, AES.MODE_CFB, master_key)
                auth_ack = auth_encryption_suite.encrypt(str(auth_ack_payload))
                return session_key, ticket_granting_ticket
            else: 
                print("UNAUTHORIZED")
        else : 
            print(response)
