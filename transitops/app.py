from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, current_user
# Combined imports from models
from models import db, User, Vehicle 

app = Flask(__name__)
app.secret_key = 'transitops_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transitops.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email, password=password, role=role).first()
        if user:
            login_user(user, remember=remember)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome {current_user.email}! Role: {current_user.role} <br> <a href='/registry'>View Vehicle Registry</a>"

@app.route('/registry')
@login_required
def registry():
    all_vehicles = Vehicle.query.all()
    return render_template('registry.html', vehicles=all_vehicles)

@app.route('/forgot-password')
def forgot_password():
    return "Password recovery page."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Seed test user
        if not User.query.filter_by(email="admin@transitops.in").first():
            db.session.add(User(email="admin@transitops.in", password="password123", role="Fleet Manager"))
            db.session.commit()
            
        # Seed test vehicles
        if not Vehicle.query.first():
            db.session.add(Vehicle(license_plate="KA-01-HC-1234", make="Ashok Leyland Dost", status="Available"))
            db.session.add(Vehicle(license_plate="MH-02-EE-5678", make="Tata Intra V30", status="On-Trip"))
            db.session.commit()

    app.run(debug=True)