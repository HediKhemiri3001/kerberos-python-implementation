"""
This script launchs a service that exposes endpoints 

"""
from flask import Flask, jsonify, request
import json
from datetime import datetime
from EncryptionHelper import EncryptionHelper


master_key = "S0m3MA5T3RK3YY"
service_secret_key = "secretsecret"
app = Flask(__name__)
eh = EncryptionHelper("ProtectedService")
@app.route('/authenticate', methods=['POST'])
def protected():
    if request.method == 'POST':
        st = request.json.get('service_ticket')
        st_plain = eh.decrypt(st, service_secret_key, master_key)
        #time_is_valid = datetime.fromtimestamp(st_plain.get('timestamp'), tz = None) - datetime.now() / 60 > int(st_plain.get('lifetime_of_ticket'))
        if st_plain.get("username") == request.json.get("username") :
            response = {"status": 204, "payload":"Authenticated and the service and client session key is %s"%st_plain.get("service_session_key")}
            return jsonify(response)
        else: 
            response = {"status": 301, "payload":"Unauthorized"}
            return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=9090)
