import requests
import time
import json
import base64
from datetime import datetime
import ast
from Crypto.Cipher import AES
from EncryptionHelper import EncryptionHelper

master_key = "S0m3MA5T3RK3YY"
eh = EncryptionHelper("Client")
def duplicate_string(input_string):
    while len(input_string) < 16:
        input_string += input_string
    return input_string[:16]
"""
Phase 1: Contact the Authentication Server by providing the user id or client id
along with the service (here, tgs) id to obtain ticket for.
"""


# construct the payload to send to authenticate server
user_name = input("Enter user id to authenticate with: ")
service_id = input("Service ID to authenticate with: ")
payload = {"username": str(user_name), "service_name": str(service_id),  "lifetime_of_tgt": "2"}
# send payload and fetch response from the authentication server
print("-" * 40)
print("Authenticating with the server...")
as_response = requests.post("http://localhost:8989/authenticate", json=payload)
time.sleep(2)
if as_response.status_code == 200:
    print("Successfully Authenticated.")
    print("-" * 40)
    response_payload = as_response.json().get('payload')
    # decode the received data
    ack_sent = response_payload.get('ack')
    ticket_granting_ticket = response_payload.get('tgt')
    # prompt for user secret key to decrypt the message
    user_secret_key = input("Your Secret Key To Decrypt: ")
    # decrypt the acknowledgement section using user secret key
    ack_plain = eh.decrypt(ack_sent, user_secret_key, master_key)

    # convert string type to dictionary type

    #json_acceptable_format = encode(ack_plain).replace("'", "\"")
    print("-" * 40)
    print ("Acknowledgement from Authentication Server")
    tgs_session_key = ack_plain.get('tgs_session_key')
    time.sleep(2)
    print("Ticket Granting Ticket from Authentication Server")
    print(ticket_granting_ticket)
    print("-" * 40)



    """
        Phase 2: Contact ticket granting server with the ticket granting
        ticket obtained from Authentication Server along with the id of the
        service to which the client is requesting ticket from the Ticket
        Granting Server.
        """
    # construct the auth payload to send to tgs
    auth_payload = {"username": str(user_name), "timestamp": str(datetime.now())}
    # encrypt the payload with tgs session key
    auth_cipher = eh.encrypt(auth_payload, ack_plain.get('tgs_session_key'), master_key)
    # prompt user for the service id

    # construct the ticket grant request for service payload
    tgr_payload = {"service_name": service_id, "lifetime_of_ticket": "2"}
    # payloads put together to send to ticket granting sever
    payload = {"authenticator": auth_cipher, "tgr": str(tgr_payload),
               "tgt": ticket_granting_ticket}
    print ("Contacting Ticket Granting Server..."  )
    tgs_response = requests.post("http://localhost:8989/ticket", json=payload)
    tgs_recieved_payload = tgs_response.json().get("payload")
    if(tgs_response.json().get("status") == 200):
        print("Recieved %s as response payload."%tgs_recieved_payload)

        # We need to decrypt the tgs_ack_ticket to get the service_session_key which we will use to communicate 
        # with the service from here on out
        tgs_ack_ticket = eh.decrypt(tgs_recieved_payload.get('tgs_ack_ticket'), tgs_session_key, master_key)
        service_ticket = tgs_recieved_payload.get("service_ticket")
        session_key = tgs_ack_ticket.get("service_session_key")
        service_payload = {"service_ticket": service_ticket, "username": user_name}
        print('-'*40)
        print("Contacting service with payload : %s"% str(service_payload))
        service_response = requests.post("http://localhost:9090/authenticate", json=service_payload)
        print(service_response.json(), session_key)
        #print("Recieved response with status %d and payload %s"%(int(service_response.json().get("status")), service_response.json().get("payload")))
    else:
        print(tgs_recieved_payload.get("message"))