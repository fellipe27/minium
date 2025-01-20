from datetime import datetime
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import os
import base64
import google.generativeai as genai

load_dotenv()

def convert_to_base_64(to_convert):
    return base64.b64encode(to_convert.picture).decode('utf-8') if to_convert.picture else None

def convert_post_created_date(date):
    aware_date = date.replace(tzinfo=ZoneInfo('UTC'))
    date_format = '%Y-%m-%d %H:%M:%S.%f%z'
    created_at = datetime.strptime(aware_date.strftime(date_format), date_format)

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

def get_post_keywords(post_content):
    genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(
        f'Obtain the keywords from: {post_content}, (just the keywords and max 3,'
        + ' and return None if there are none)'
    ).text.replace('\n', '').split(', ')

    return response if len(response) > 1 and 'None' not in response else []

def create_post_object(post):
    return {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'created_at': post.created_at.date(),
        'author_picture': convert_to_base_64(post.author),
        'image': convert_to_base_64(post),
        'comments': len(post.comments.all()),
        'claps': post.claps_count()
    }
