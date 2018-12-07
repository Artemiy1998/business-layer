from suds.client import Client

from .update import Schedule

hello_client = Client('http://localhost:8000/service')

sh = Schedule()

sh.

print(hello_client.service.setet_scenario())
