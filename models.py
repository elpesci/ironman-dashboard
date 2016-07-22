from flask.ext.mongoengine import MongoEngine
from mongoengine import *
import datetime
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.clients
coll = db.cliente


connect("clients", alias="default", host="127.0.0.1", port=27017)


# Create models
db = MongoEngine()

# DOCUMENTS

class Cliente(db.Document):
    nombre = db.StringField()
    login = db.StringField()
    descripcion = db.StringField()
    estados = db.ListField(db.ReferenceField('Estado'))
    payment_date = db.DateTimeField()
    contract = db.IntField()
    payment_expiration_date = db.DateTimeField(default=datetime.datetime.now)
    password = db.StringField()

    meta = {"db_alias": "default"}

    def __unicode__(self):
        return self.nombre

    def payment_status_ok(self):
        return self.payment_expiration_date > datetime.datetime.now()

class Estado(db.Document):
    codigo = db.StringField(max_length=5)
    nombre = db.StringField()

    meta = {"db_alias": "default"}

    # Required for administrative interface
    def __unicode__(self):
        return self.nombre


def get_client_from_username(username):
    return Cliente.objects(login=username).first()

