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
master_key = "S0m3MA5T3RK3YY"
class KDC:
    def __init__(self):
        self.AS = AuthenticationServer(master_key)



kdc = KDC()
kdc.AS.login("hedi","hedi","tomcat")