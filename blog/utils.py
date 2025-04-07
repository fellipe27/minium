from zoneinfo import ZoneInfo
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import base64

def get_post_keywords(post):
    try:
        texts = [post.title, post.story]

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(texts)

        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[-1]

        word_scores = list(zip(feature_names, scores))
        keywords = sorted(word_scores, key=lambda x: x[1], reverse=True)[:3]

        return [word for word, score in keywords]
    except ValueError:
        return []

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

def convert_user(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'birthday': user.birthday,
        'picture': base64.b64encode(user.picture).decode('utf-8') if user.picture else None,
        'bio': user.bio
    }

def convert_post(post, user):
    return {
        'id': post.id,
        'title': post.title,
        'story': post.story,
        'author': post.author,
        'created_at': convert_post_created_date(post.created_at),
        'picture': base64.b64encode(post.picture).decode('utf-8') if post.picture else None,
        'claps': {
            'amount': post.claps_amount(),
            'already_clap': post.user_liked_post(user)
        },
        'comments': {
            'amount': post.comments.all().count(),
            'responses': [
                {
                    'id': comment.id,
                    'content': comment.content,
                    'author': convert_user(comment.author),
                    'created_at': comment.created_at.date()
                } for comment in post.comments.all()
            ]
        }
    }
