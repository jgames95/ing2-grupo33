def authenticated(session):
    return session.get("user_id")


def is_active(session):
    return session.get("active")
