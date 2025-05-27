Dette systemet krever noe videre oppsett med raspberry pi.
Det vil derfor ikke fungere helt out of the box. 

Det må settes opp NGINX webserver, flask server og gunicorn som håndterer flask og kommunikasjon mellom NGINX og Flask. 

Frontend filer må legges i html mappen på webserver

Backend filer må legges i flask_app folder på home folder

Config filer må settes opp for NGINX og Gunicorn.

For vaslinger og brukergrensnitt på internett over https, over port 443 må være åpnet.
