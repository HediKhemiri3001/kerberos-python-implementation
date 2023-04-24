"""
This script is responsible for handling Authentication across a database,
using the AuthenticationServer helper class.
Also responsible for calling the methods of the TicketGrantingService Helper class.
And handling errors
Expected Functionalities:
- Generate session keys for each principal and store them.
- Call Authentication server login on recieving login request.
- Call ServiceTicketGrant in TicketGrantingService
Expected errors:
- Wrong Credentials.

"""
from authentication_server import AuthenticationServer
from db_helper import DBHelper
from ticket_granting_service import TicketGrantingService
from flask import Flask, jsonify, request
import json


master_key = "S0m3MA5T3RK3YY"

app = Flask(__name__)

AS = AuthenticationServer(master_key)
TGS = TicketGrantingService(master_key)
@app.route('/authenticate', methods=['POST'])
def authentication_server():
    if request.method == 'POST':
        user_name = request.json.get('username')
        service_name = request.json.get('service_name')
        lifetime_of_tgt = request.json.get('lifetime_of_tgt')
        status, payload = AS.login(user_name,service_name,2)
        if status == 1:
            response = {"status":200, "payload": payload}

            return jsonify(response)
        else:
            response = {"status":404, "payload": {"message": "User not found."}}

@app.route('/ticket', methods=['POST'])
def ticket_granting_server():
    if request.method == 'POST':
        tgt = request.json.get("tgt")
        authenticator = request.json.get("authenticator")
        tgr = request.json.get("tgr")
        status, payload = TGS.process(authenticator, tgt, tgr)
        if status == 1:
            response = {"status":200, "payload": payload}

            return jsonify(response)
        elif status == -1:
            response = {"status": 404, "payload": {"message":payload}}
            return jsonify(response)
        elif status == -2:
            response = {"status": 304, "payload": {"message":payload}}
            return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=8989)
