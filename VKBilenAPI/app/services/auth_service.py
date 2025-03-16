from app.models import db, API


def create_api_key(user_name, user_mail):
    new_key = API(user_name=user_name, user_mail=user_mail)
    db.session.add(new_key)
    db.session.commit()
    return new_key.api_key


def verify_api_key(api_key):
    return API.query.filter_by(api_key=api_key).first() is not None
