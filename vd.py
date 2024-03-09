#VenkyDeexu18
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model

vd = Flask(__name__)
vd.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
vd.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
vd.config['UPLOAD_FOLDER'] = 'uploads'
vd.secret_key = 'venkydeexu18'

db = SQLAlchemy(vd)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(99), unique=True, nullable=False)
    password = db.Column(db.String(99), nullable=False)
    name = db.Column(db.String(99), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)

def create_app():
    db.init_app(vd)
    vd.app_context().push()
    db.create_all()

create_app()

model = load_model('model.h5')

lesion_type_dict = {
    0: 'Melanocytic nevi',
    1: 'Melanoma',
    2: 'Benign keratosis-like lesions',
    3: 'Basal cell carcinoma',
    4: 'Actinic keratoses',
    5: 'Vascular lesions',
    6: 'Dermatofibroma'
}

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (100, 75))
    img = img / 255.0  
    img = np.expand_dims(img, vdis=0)  
    return img

def predict_skin_cancer(image_path):
    processed_image = preprocess_image(image_path)
    predictions = model.predict(processed_image)
    predicted_class = np.argmvd(predictions)
    predicted_type = lesion_type_dict[predicted_class]
    return predicted_type

@vd.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        name = request.form['name']
        phone_number = request.form['phone']
        if not User.query.filter_by(email=email).first():
            new_user = User(email=email, password=password, name=name, phone_number=phone_number)
            db.session.add(new_user)
            db.session.commit()
            session['name'] = name
            create_user_folder(email)
            return redirect(url_for('home', name=name))
        else:
            return 'Email already exists. Choose a different one.'
    return render_template('index.html')

@vd.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['name'] = user.name
            return redirect(url_for('home', name=user.name))
        else:
            return 'Login failed Dude! Check your email and password.'
    return render_template('index.html')

@vd.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'Yoo! No file selected'
    file = request.files['image']
    if file.filename == '':
        return 'Select something Dude!'
    email = User.query.filter_by(name=session.get('name')).first().email
    create_user_folder(email)
    file_path = os.path.join(vd.config['UPLOAD_FOLDER'], email, file.filename)
    file.save(file_path)
    predicted_type = predict_skin_cancer(file_path)
    return render_template('main.html', name=session.get('name'), predicted_type=predicted_type)

@vd.route('/home')
def home():
    name = session.get('name')
    if not name:
        return redirect(url_for('login'))
    return render_template('main.html', name=name)

@vd.route('/logout')
def logout():
    session.pop('name', None)
    return redirect(url_for('signup'))

def create_user_folder(email):
    folder_path = os.path.join(vd.config['UPLOAD_FOLDER'], email)
    os.makedirs(folder_path, exist_ok=True)

if __name__ == '__main__':
    vd.run(debug=True, port=1718)
