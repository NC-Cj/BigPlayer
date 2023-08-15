from db.db import session


def insert(data):
    session.add(data)
    session.commit()
    session.close()
