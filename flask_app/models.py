from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(unique=True, required=True)
    email = db.EmailField(unique=True, required=True)
    password = db.StringField(required=True) # Added required
    profile_pic = db.ImageField()

    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class Item(db.Document):
    creator = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    name = db.StringField(required=True, min_length=1, max_length=100)
    item_id = db.StringField(required=True, min_length=5, max_length=500)
    likes = db.IntField(required=True, min_value=0, max_value=9999)

    # Returns unique string identifying our object
    def get_id(self):
        return self.name + self.date


class ItemComment(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    item_id = db.StringField(required=True, length=9)


class Creature(db.Document):
    creator = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    name = db.StringField(required=True, min_length=1, max_length=100)
    creature_id = db.StringField(required=True, min_length=5, max_length=500)
    likes = db.IntField(required=True, min_value=0, max_value=9999)

    # Returns unique string identifying our object
    def get_id(self):
        return self.name + " " + self.date


class CreatureComment(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    creature_id = db.StringField(required=True, length=9)