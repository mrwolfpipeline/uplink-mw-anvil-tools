import anvil.server
from shotgun_api3 import Shotgun
import shotgun_api3
from tank.authentication import ShotgunAuthenticator, set_shotgun_authenticator_support_web_login
import os
import time_off_requests


SERVER_PATH = os.getenv("MW_PYTHON_SHOTGRID_SERVER")
SCRIPT_NAME = os.getenv("MW_PYTHON_SHOTGRID_NAME")
SCRIPT_KEY = os.getenv("MW_PYTHON_SHOTGRID_KEY")

ANVIL_UPLINK_KEY = os.getenv("ANVIL_UPLINK_KEY")

@anvil.server.callable
def get_shotgrid_user():
    Shotgun.NO_SSL_VALIDATION = True
    sa = ShotgunAuthenticator()
    user = sa.get_default_user()

    if not user:
        print('No ShotGrid User found...Please log in using SG Desktop.')
        set_shotgun_authenticator_support_web_login(True)
        authenticator = ShotgunAuthenticator()
        user = authenticator.get_user_from_prompt()

    user_login = user.login

    sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

    fields = ['id', 'name', 'email', 'permission_rule_set', 'firstname', 'lastname', 'sg_office_code',
              'sg_software' , 'sg_mw_anvil_alignment']

    user_data = sg.find_one('HumanUser', [['login', 'is', user_login]], fields)

    return user_data

@anvil.server.callable
def get_shotgrid_projects():
    sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

    filters = [['sg_status', 'is', 'Active'], ['sg_project_folder', 'is', 'Overhead']]
    fields = ['name', 'id']
    projects = sg.find("Project", filters, fields)

    project_list = [(project['name'], project['id']) for project in projects]

    project_list.sort(key=lambda project: project[0])

    return project_list

def get_sg_status_icons(sg):
    if sg is None:
        sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

    fields = ['bg_color', 'icon', 'code', 'name', 'sg_status_list_map_icon', 'data', 'image', 'thumbnail_path', 'thumbnail', 'image_data', 'entity', 'thumb']
    statuses = sg.find('Status', [], fields)

    return statuses

if __name__ == "__main__":
    # submit_time_off_request(129, "2024-10-17", "2024-10-17", 4, 4, 1386, "TEST CHAD SUBMISSION")

    books = time_off_requests.load_time_off_requests(129, 'cfrm')
    sorted_data = sorted(books, key=lambda x: x['created_at_object'])
    for book in books:
        print(book['created_at'])

    # get_sg_status_icons(sg=None)

    anvil.server.connect(ANVIL_UPLINK_KEY)
    anvil.server.wait_forever()