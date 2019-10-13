from myproject import db
from flask import render_template, redirect, request, url_for, flash,abort
from flask_login import login_user,login_required,logout_user
from myproject.models import User, build_model, predict_image
from myproject.forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
import os
from flask import Flask
#import tensorflow as tf # Import to build the graph for the model

#stripe_keys = {
#  'secret_key': os.environ['STRIPE_SECRET_KEY'],
#  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
#}
#stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__, template_folder='/myproject/templates',static_folder='/myproject/static')

#model = build_model() # Build the model with the specific json and h5 weights file
#graph = tf.get_default_graph() # Get the default graph from tensorflow


STRIPE_PUBLISHABLE_KEY = 'pk_test_AqeZev5riTgYUBXShKNJiZDG00Rdbu7N2j'
STRIPE_SECRET_KEY  = "sk_test_gKdEhmMzNfb5QLs3Cipeqa0J00caKSwmXI"
stripe.api_key=STRIPE_SECRET_KEY

@app.route('/')
def home():
    return render_template('/myproject/templates/index.html',key=STRIPE_PUBLISHABLE_KEY)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if 'file' not in request.files:
        return render_template('welcome_user.html',predictions=[])

    file = request.files['file']
    if file.filename =='':
        return render_template('welcome_user.html',predictions=[])

    if file and allowed_file(file.filename):
        global graph
        with graph.as_default():
            predictions = predict_image(model, file)
        return render_template('image_upload.html', predictions=list(predictions))

    return render_template('welcome_user.html', predictions=[])

@app.route('/welcome')
@login_required
def welcome_user():
    return render_template('welcome_user.html', key=STRIPE_PUBLISHABLE_KEY)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out!')
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object

        if user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('home')

            return redirect(next)
    return render_template('login.html', form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering! Now you can login!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/payment', methods=['POST'])
def payment():

    # CUSTOMER INFORMATION
    customer = stripe.Customer.create(email='sample@customer.com',
                                      source=request.form['stripeToken'],)

    # CHARGE/PAYMENT INFORMATION
    stripe.Charge.create(
        customer=customer.id,
        amount=1099,
        currency='usd',
        description='purchase'
    )
    #Need to update in database

    has_paid = 'Y'

    return redirect(url_for('welcome_user'),variable=has_paid)

@app.route('/file_upload', methods=['POST'])
def fileupload():
    return redirect(url_for('welcome_user'))


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
