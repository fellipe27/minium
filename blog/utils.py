from datetime import datetime
import base64

def convert_to_base_64(image):
    return base64.b64encode(image).decode('utf-8')

def convert_post_created_date(date):
    date_format = '%Y-%m-%d %H:%M:%S.%f%z'
    created_at = datetime.strptime(str(date), date_format)

    now = datetime.now(created_at.tzinfo)
    time_diff = now - created_at

    days = time_diff.days
    seconds = time_diff.total_seconds()
    hours = int(seconds // 3600)
    minutes = int((seconds // 60) % 60)

    if days > 0:
        result = f'{days} day(s) ago'
    elif hours > 0:
        result = f'{hours} hour(s) ago'
    elif minutes > 0:
        result = f'{minutes} minute(s) ago'
    else:
        result = 'Few seconds ago'

    return result
