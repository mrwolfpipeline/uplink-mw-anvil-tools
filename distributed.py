import anvil.server
import shotgun_api3
import uplink
import datetime

machine_name = "NEPTUNE"

@anvil.server.callable("launch_" + machine_name )
def example_func():
  print("CALLING CHAD NEPTUNE")
  return