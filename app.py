from flask import Flask,render_template,request,session,redirect,url_for,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user,login_manager,LoginManager
import pandas as pd
from sklearn.linear_model import LinearRegression
from flask import redirect
import joblib
model = LinearRegression()


model=joblib.load('spp_model.joblib')


local_server = True
app = Flask(__name__)
app.secret_key='umair'

login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/spp'
app.config['SQLALCHEMY_Modifications']=False
db=SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True ,autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
    


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)
        newuser=User(email=email,username=username,password=encpassword)
        db.session.add(newuser)
        db.session.commit()
        flash("Signup Succes Please Login","success")
        return render_template('login.html')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        email = request.form.get('email')
        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash("Login Succes","success")
                return render_template('index.html')
            else:
                flash("Password is Incorrect","warning")
                return render_template('login.html')
        else:

            flash("Email is Incorrect","warning")
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Succes","success")
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/model')
def model_vew():
    return render_template('model.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()

        flash("Form submitted successfully!", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Get input data from the form
        features = {
            'Weekly_Study_Hours': float(request.form['Weekly_Study_Hours']),
            'Attendance Percentage': float(request.form['Attendance Percentage'])

        }

        # Convert the input data into a DataFrame
        input_data = pd.DataFrame([features])

        # Make predictions using the trained model
        predicted_gpa = model.predict(input_data)

        return render_template('result.html', predicted_gpa=predicted_gpa[0])


if __name__ == '__main__':
    app.run(debug=True)





 



