# Kerberos project

- [ ] Implement KDC Prototype
- [ ] Implement TGS, and Authentication
- [ ] Implement a service server
- [ ] Implement an interface for the client to use.

## Overview

In this project we need to implement the kerberos infrastructure for authentication, to access a ressource.
This image provides an overview of the architecture.

We have 3 main actors :

1. The client or principal.
2. The application server that provides access to the ressource.
3. A KDC (Key Distribution Center)

In this project we will elaborate python scripts that each acts as a part of the Kerberos architecture just to practice implementing it.
We will use the module provided for python, called Kerberos-python.

## KDC

The KDC process provides 2 services, an authentication service and a ticket granting service.
