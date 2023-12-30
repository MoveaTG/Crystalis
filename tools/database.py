from peewee import *
import datetime
import logging
import json

db = SqliteDatabase('./databases/database.db')

with open('config.json', 'r', encoding='utf8') as f:
    config = json.load(f)
def init() -> None:
    logging.info('База данных была инициализирована')

    db.connect()
    db.create_tables([User, Film, Channels])

    for admin in config["admin_id"]:
        User.get_or_create(id=admin, isAdmin=True)


def check_admin(user_id: int) -> bool:
    user = User.get_or_none(id=user_id)

    if user.isAdmin:
        return True

    return False


def get_users_for_day() -> int:
    now = datetime.datetime.today()
    users = User.select().where(User.firstUse.day == now.day).count()
    return users


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = IntegerField(unique=True)
    isAdmin = BooleanField(null=True)
    firstUse = DateField(null=True, default=datetime.datetime.today())


class Film(BaseModel):
    id = IntegerField(unique=True)
    name = CharField(null=True)
    description = CharField(null=True)


class Channels(BaseModel):
    id = IntegerField(unique=True)
    emoji = CharField(null=True)