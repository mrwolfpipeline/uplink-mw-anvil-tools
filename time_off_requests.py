import anvil.server
import shotgun_api3
import uplink
import datetime
from datetime import datetime

SERVER_PATH = uplink.SERVER_PATH
SCRIPT_NAME = uplink.SCRIPT_NAME
SCRIPT_KEY = uplink.SCRIPT_KEY

ANVIL_UPLINK_KEY = uplink.ANVIL_UPLINK_KEY

@anvil.server.callable
def load_time_off_requests(user_id, status=None):
    sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

    if status is None:
        filters = [['user.HumanUser.id', 'is', user_id], ['vacation', 'is', True]]
    else:
        filters = [['user.HumanUser.id', 'is', user_id], ['sg_status_list', 'is', status], ['vacation', 'is', True]]

    fields = ['start_date', 'end_date', 'sg_unpaid_days_requested', 'sg_status_list', 'sg_paid_days_requested', 'note', 'vacation', 'user', 'user.HumanUser.id', 'created_at']

    found_bookings = sg.find('Booking', filters, fields)


    def format_date(date_str=None, date_obj=None):
        date_format = '%a %b %d %Y'

        if date_str is not None:
            new_date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Convert string to datetime
            return new_date_obj.strftime(date_format)

        if date_obj is not None:
            return date_obj.strftime(date_format)

    def build_date_object(date_str):
        date_format = "%a %b %d %Y"
        date_obj = datetime.strptime(date_str, date_format)
        return date_obj

    status_data = uplink.get_sg_status_icons(sg)

    for item in found_bookings:
        for key, value in item.items():
            if value is None or value == 0:
                item[key] = ""
        item['start_date'] = format_date(date_str=item['start_date'])
        item['end_date'] = format_date(date_str=item['end_date'])
        item['created_at_object'] = item['created_at']
        item['created_at'] = format_date(date_obj=item['created_at'])
        item['start_date_object'] = build_date_object(item['start_date'])
        item['end_date_object'] = build_date_object(item['start_date'])
        item['show_trash'] = check_date_passed(item['start_date'])

        status_code = item.get('sg_status_list')  # Get the sg_status_list from the current item
        matching_status = next((status for status in status_data if status['code'] == status_code), None)

        if matching_status:
            if matching_status['bg_color'] is not None:
                item['bg_color'] = matching_status['bg_color']
            else:
                item['bg_color'] = '179,179,179'

            item['icon_name'] = matching_status['icon'].get('name')

            if item['icon_name'] is not None:
                item['icon_path'] = '_/theme/icons/' + item['icon_name'] + '.png'

            else:
                item['icon_path'] = '_/theme/' + 'mrwolf' + '.png'

    return found_bookings

def check_date_passed(start_date):
    date_format = "%a %b %d %Y"

    # Convert the 'start_date' string into a datetime object
    start_date_obj = datetime.strptime(start_date, date_format)

    # Get today's date (no time included)
    today_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    # Check if start_date is less than or equal to today
    if start_date_obj <= today_date:
        show_trash = False

    else:
        show_trash = True

    return show_trash



@anvil.server.callable()
def submit_time_off_request(user_id, start_date, end_date, unpaid_days, paid_days, note):
    sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

    vacation = True

    if paid_days is None:
        paid_days = 0.0

    else:
        paid_days = float(paid_days)

    if unpaid_days is None:
        unpaid_days = 0.0

    else:
        unpaid_days = float(paid_days)

    booking_data = {
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

@anvil.server.callable
def delete_time_off_request(booking_id):
    sg = shotgun_api3.Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
    sg.delete("Booking", booking_id)