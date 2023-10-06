# Kerberos python implementation.

In the context of cosolidating knowledge and lessons about cyber security, this project's goal is to further our understanding about this protocol.

## Functionality
This repo offers an API representing the KDC exposing /authenticate and /ticket endpoints, each of these represents respectively the Authentication Service and the Ticket Granting Service. A client wanting to be authenticated will send a payload including his username and the service with which he wants to authenticate. The client is then prompted for his password which is his secret key in the Kerberos architecture. The KDC Api then handles that request and matches the client with his information stored in a Sqllite database, and starts the kerberos authentication protocol process, we start by returning to the client requesting to /authenticate a Auth_ack containing the session key and various other information between the TGS and the client encrypted with the client's secret key, a ticket granting ticket is also returned to the client, this ticket is then sent as is to the TGS through the /ticket endpoint, this endpoint then returns a Service Ticket encrypted with the requested service's secret key, that is then sent by the client to the requested service's server for authentication with that server, note that all these tickets are timestamped and controlled to further secure this process.
The requested service is represented as an API that can be hosted on a seperate machine in this project.

So in conclusion, we have 3 main Principals which are : 
 1. The client: sends requests to the 2 endpoints of the KDC API, and uses the information returned to resend it to other endpoints.
 2. The KDC: represented as a Flask API that exposes 2 endpoints /authenticate and /ticket which each act as one of the 2 main services requires by a KDC. Note that these endpoints can be seperated into 2 seperate APIs if we want to.
 3. The protected ressource: in this repo is represented by an API that only returns the requested values if the client requesting is successfully authenticated.

Following this architecture:
![Image explaining the architecture](https://media.geeksforgeeks.org/wp-content/uploads/20190711134228/Capture6663.jpg)

Except that the server and Kerberos entities are both declared in this repository.
This is a working project and I envision many improvements whenever We find the time.
## Credits 
This repository was elaborated by:
 - KHEMIRI Mohamed Hedi
 - DALI HASSEN Naim
 - CHENIOUR Emna
 - SMAOUI Youssef

## TODOS

- [x] Database helper functions.
- [x] AuthenticationService of the KDC
- [x] TicketGrantingService of the KDC
- [x] Master API for the KDC
- [x] Create the service that's being protected
- [x] Implement client side script to access this ressource service if authenticated.

> This project is majorly influenced by [this repository](https://github.com/PrasannaVenkadesh/kerberos-auth-tgs-prototype).
