from app.models import db, Payment


def add_payment(user_id, amount):
    new_payment = Payment(user_id=user_id, amount=amount)
    db.session.add(new_payment)
    db.session.commit()
    return {"message": "Payment successful"}
