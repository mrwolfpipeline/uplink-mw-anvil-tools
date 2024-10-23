import anvil.server
import shotgun_api3
import uplink
import datetime

machine_name = "CHAD NEPTUNE"

@anvil.server.callable("example_func" + machine_name )
def example_func():
  print("CALLING CHAD NEPTUNE")
  return