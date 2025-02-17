from app.models import db, APIKey


def create_api_key(user_name):
    new_key = APIKey(user_name=user_name)
    db.session.add(new_key)
    db.session.commit()
    return new_key.api_key


def verify_api_key(api_key):
    return APIKey.query.filter_by(api_key=api_key).first() is not None
