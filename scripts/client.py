import requests
import time
import json
import base64
from datetime import datetime
import ast
from Crypto.Cipher import AES


master_key = "S0m3MA5T3RK3YY"

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
payload = {"username": str(user_name), "service_name": "tgs",  "lifetime_of_tgt": "2"}
# send payload and fetch response from the authentication server
print("-" * 40)
print("Authenticating with the server...")
as_response = requests.post("http://localhost:8989/authenticate", json=payload)
time.sleep(2)
if as_response.status_code == 200:
    print("Successfully Authenticated.")
    print("-" * 40)
    response_payload = as_response.json().get('payload')
    print(response_payload)
    # decode the received data
    ack_sent = base64.b64decode(response_payload.get('ack')[1:])
    ticket_granting_ticket = response_payload.get('tgt')[1:]
    # prompt for user secret key to decrypt the message
    user_secret_key = input("Your Secret Key To Decrypt: ")
    # decrypt the acknowledgement section using user secret key
    ack_dec_suite = AES.new(duplicate_string(user_secret_key).encode('utf8'), AES.MODE_CFB, duplicate_string(master_key).encode('utf8'))
    ack_plain = ack_dec_suite.decrypt(ack_sent)
    # convert string type to dictionary type

    #json_acceptable_format = encode(ack_plain).replace("'", "\"")
    ack_plain = json.loads(str(ack_plain)[1:])
    ack_plain_dict = ast.literal_eval(ack_plain)
    print("-" * 40)
    print ("Acknowledgement from Authentication Server")
    print (type(ack_plain_dict))
    time.sleep(2)
    print("\nTicket Granting Ticket from Authentication Server")
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
    auth_enc_suite = AES.new(ack_plain_dict.get('tgs_session_key').encode('utf8'), AES.MODE_CFB, duplicate_string(master_key).encode('utf8'))
    auth_cipher = auth_enc_suite.encrypt(str(auth_payload).encode("utf8"))
    # prompt user for the service id
    service_id = input("Service ID: ")
    # construct the ticket grant request for service payload
    tgr_payload = {"service_name": service_id, "lifetime_of_ticket": "2"}
    # payloads put together to send to ticket granting sever
    payload = {"authenticator": str(base64.b64encode(auth_cipher)), "tgr": str(tgr_payload),
               "tgt": ticket_granting_ticket}
    print ("Contacting Ticket Granting Server..."  )   
    print("Sending payload:", str(payload))   
    tgs_response = requests.post("http://localhost:8989/ticket", json=payload)
    print(str(tgs_response))