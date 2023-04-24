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
import json
import base64
from datetime import datetime
from Crypto.Cipher import AES
from EncryptionHelper import EncryptionHelper
class AuthenticationServer:
    def __init__(self, masterkey):
        self.db = DBHelper()
        self.masterkey = masterkey
        self.eh = EncryptionHelper("AuthenticationService")
    def duplicate_string(self,input_string):
        while len(input_string) < 16:
            input_string += input_string
        return input_string[:16]
    def login(self,username, service, lifetime_of_tgt=10000000):
        status, response = self.db.fetch_user(username)
        if status == 1:
            # Get TGS info.
            status , tgs_service = self.db.fetch_service("tgs")
            tgs_secret_key = tgs_service.get_secret_key()
            # Generate session key.
            user_tgs_session_key = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])[0:16]
            # Authentication acknowledgement payload.
            auth_ack_payload = {"service_id": "tgs", "timestamp": str(datetime.now()), 
            "lifetime": str(lifetime_of_tgt), "tgs_session_key": str(user_tgs_session_key)}
            # TicketGrantingTicket payload
            tgt_payload = {"username": str(username), "service_id": str(service), "timestamp": str(datetime.now()), 
               "lifetime": str(lifetime_of_tgt), "tgs_session_key": str(user_tgs_session_key)}
            # Encrypting the TGT Payload.
            ticket_granting_ticket = self.eh.encrypt(tgt_payload, tgs_secret_key, self.masterkey)
            # Encrypting the AuthAck payload.
            auth_ack = self.eh.encrypt(auth_ack_payload, response.get_password(), self.masterkey)
            final_payload = {"ack": auth_ack, "tgt": ticket_granting_ticket}
            return 1, final_payload
        else : 
            return -1,"User not found."
