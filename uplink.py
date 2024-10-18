from datetime import datetime
import os
import anvil.server
from shotgun_api3 import Shotgun
import shotgun_api3
import sgtk
from tank.authentication import ShotgunAuthenticator, set_shotgun_authenticator_support_web_login

SERVER_PATH = "https://mrwolf.shotgunstudio.com/"
SCRIPT_NAME = "mw_python"
SCRIPT_KEY = os.getenv("MW_PYTHON_SHOTGRID")

anvil_uplink_key = os.getenv("ANVIL_UPLINK_KEY")

anvil.server.connect(anvil_uplink_key)


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

    user_data = sg.find_one('HumanUser', [['login', 'is', user_login]], ['id', 'name'])
    user_id = user_data['id']
    user_name = user_data['name']

    return user_login, user_id, user_name

@anvil.server.callable
def get_shotgrid_projects():
    sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

    filters = [['sg_status', 'is', 'Active'], ['sg_project_folder', 'is', 'Overhead']]
    fields = ['name', 'id']
    projects = sg.find("Project", filters, fields)

    project_list = [(project['name'], project['id']) for project in projects]

    project_list.sort(key=lambda project: project[0])

    return project_list

@anvil.server.callable()
def submit_time_off_request(user_id, start_date, end_date, unpaid_days, paid_days, project_id, note):
    sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

    vacation = True
    print(user_id, start_date, end_date, unpaid_days, paid_days, project_id, note)

    if paid_days is None:
        paid_days = 0.0

    else:
        paid_days = float(paid_days)

    if unpaid_days is None:
        unpaid_days = 0.0

    else:
        unpaid_days = float(paid_days)

    booking_data = {
        # 'project': {'type': 'Project', 'id': project_id},  # Replace with your project ID
        'user': {'type': 'HumanUser', 'id': user_id},  # Replace with your resource (user) ID
        'start_date': start_date,
        'end_date': end_date,
        'sg_unpaid_days_requested': unpaid_days,
        'sg_paid_days_requested': paid_days,
        'note': note,
        'vacation': vacation
    }

    sg.create('Booking', booking_data)

    return "Time Off Request Submitted!"

if __name__ == "__main__":
    # submit_time_off_request(129, "2024-10-17", "2024-10-17", 4, 4, 1386, "TEST CHAD SUBMISSION")
    # get_shotgrid_user()
    anvil.server.wait_forever()