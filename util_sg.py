import anvil.server
from shotgun_api3 import Shotgun
import shotgun_api3
from tank.authentication import ShotgunAuthenticator, set_shotgun_authenticator_support_web_login
import os

SERVER_PATH = os.getenv("MW_PYTHON_SHOTGRID_SERVER")
SCRIPT_NAME = os.getenv("MW_PYTHON_SHOTGRID_NAME")
SCRIPT_KEY = os.getenv("MW_PYTHON_SHOTGRID_KEY")

ANVIL_UPLINK_KEY = os.getenv("ANVIL_UPLINK_KEY")

sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)


# Where entity_fields is a list of fields that are of entities
@anvil.server.callable
def sg_find(entity, filters, fields):
    # sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
    found_data = sg.find(entity, filters, fields)

    return found_data

@anvil.server.callable
def sg_get_schema(entity):
    entity_fields = sg.schema_field_read(entity)

    return entity_fields