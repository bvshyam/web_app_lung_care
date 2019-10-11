from myproject import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
import numpy as np
#import tensorflow as tf
from keras.preprocessing import image
from keras.models import Sequential, model_from_json
import json

# By inheriting the UserMixin we get access to a lot of built-in attributes
# which we will be able to call in our views!
# is_authenticated()
# is_active()
# is_anonymous()
# get_id()


# The user_loader decorator allows flask-login to load the current user
# and grab their id.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):

    # Create a table in the db
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        # https://stackoverflow.com/questions/23432478/flask-generate-password-hash-not-constant-output
        return check_password_hash(self.password_hash,password)

def build_model():
  with open('model_results/multi_disease_model.json', 'r') as json_file:
    architecture = json.load(json_file)
    model = model_from_json(json.dumps(architecture))

  model.load_weights('model_results/multi_disease_model_weight.h5')
  model._make_predict_function()
  return model

def load_image(img_path):
  img = image.load_img(img_path, target_size=(128, 128, 3))
  img = image.img_to_array(img)
  img = np.expand_dims(img, axis=0)
  img /= 255.
  return img


def predict_image(model,img_path):
    new_image = load_image(img_path)
    pred = model.predict(new_image)
    return np.argmax(pred)
