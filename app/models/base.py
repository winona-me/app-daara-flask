from app.extension import db

class BaseModel(db.Model):
    __abstract__ = True

    cree_le = db.Column(db.DateTime, server_default=db.func.now())
    maj_le = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())