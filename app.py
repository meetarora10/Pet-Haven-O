import re
import eventlet
eventlet.monkey_patch()

import random, os
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import Booking, Cart, Competition, Dog, DogDetails, Service, TimeSlot, Trainer, TrainerEditRequest, UserDetails, Wishlist, db, User, Notification,TrainerInfo,Revenue
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from flask_migrate import Migrate
from random import randint
from datetime import datetime, timedelta, timezone
import logging
from sqlalchemy import func

## team 3 imports

from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
#Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_heaven.db?timeout=10'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'alpha'
# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'companypethaven@gmail.com'
app.config['MAIL_PASSWORD'] = 'adgz kwhe mchu mrnj'
# Define the upload folder path in your config
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads folder exists (create if it doesn't)
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
# Initialize extensions
db.init_app(app)
mail = Mail(app)
socketio = SocketIO(app)

#team3 extension
migrate = Migrate(app, db)


# Initialize Flask-Login's LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# Create the database

with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Check if there are any existing competitions in the database
        if not Competition.query.first():
            # Define the services list if the database is empty
            services = [
                Competition(
                    title="Agility Challenge",
                    date="24-03-2025",
                    time="10:00 am",
                    description="Test your dog's ability to complete an obstacle course following the commands.",
                    price=500
                ),
                Competition(
                    title="Obedience Trial",
                    date="25-03-2025",
                    time="12:00 am",
                    description="Dog and handler perform a series of obedience exercises to demonstrate their training.",
                    price=600
                ),
                Competition(
                    title="Best Costume Show",
                    date="26-03-2025",
                    time="12:00 am",
                    description="Elegant Tails, Happy Hearts",
                    price=700
                ),
            ]
            
            # Add the services to the database and commit
            db.session.add_all(services)
            db.session.commit()
            logger.info("Initial services added successfully")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")


with app.app_context():
    db.create_all()

#team3 

# Initialize database with app context
with app.app_context():
    db.create_all()

    # Populate the database with sample data (Run only once)
    if not Service.query.first():
        services = [
            Service(service_name="Grooming", duration="1 hour", cost=50.0, description="Treat your dog to ultimate relaxation with our soothing therapy sessions. Tailored to calm and rejuvenate, it's the paw-fect way to unwind"),
            Service(service_name="Relaxation Therapy", duration="45 minutes", cost=40.0, description="Keep your furry friend looking and feeling their best with our professional dog grooming services. From baths to stylish trims, we pamper your pet with care"),
            Service(service_name="Health Care", duration="30 minutes", cost=30.0, description="Ensure your dog's health and happiness with our comprehensive healthcare services. From regular check-ups to expert treatments, we've got them covered"),        
        ]
        db.session.add_all(services)
        db.session.commit()

        # trainers = [
        #     Trainer(tname="John Doe", experience="5 years", rating=4.5, description="Expert groomer.", profile_pic="../static/images/man1.jpg", service_id=1),
        #     Trainer(tname="Jane Smith", experience="3 years", rating=4.8, description="Specializes in relaxation techniques.", profile_pic="../static/images/man2.jpg", service_id=2),
        #     Trainer(tname="Michael Johnson", experience="7 years", rating=4.7, description="Veteran in pet grooming and hygiene.", profile_pic="../static/images/man3.jpg", service_id=1),
        #     Trainer(tname="Emily Brown", experience="4 years", rating=4.9, description="Expert in pet relaxation therapy.", profile_pic="../static/images/man4.jpg", service_id=2),
        #     Trainer(tname="David Wilson", experience="6 years", rating=4.6, description="Provides excellent healthcare guidance for pets.", profile_pic="../static/images/man5.jpg", service_id=3),
        # ]
        # db.session.add_all(trainers)
        # db.session.commit()

        slots = [
        "09:00 AM", "10:00 AM", "11:00 AM",
        "02:00 PM", "03:00 PM", "04:00 PM"
        ]
        for slot in slots:
          if not TimeSlot.query.filter_by(time_slot=slot).first():
            db.session.add(TimeSlot(time_slot=slot))
            db.session.commit()


#team 5
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Insert sample data
        sample_data = [
            # Example 1: Dog Sale + Training + Competition
            Revenue(
                date="2022-01-07",
                revenue_type="All",  # All three services
                dog_name="Golden Retriever",
                dog_sales=45000,  # Dog sale amount
                trainer_name="John Doe",
                commission=7500,  # Training commission
                competition_name="Agility Championship",
                competition_amount=10000,  # Competition earnings
            ),
            # Example 2: Dog Sale + Training
            Revenue(
                date="2022-01-08",
                revenue_type="Dog Sales & Training",
                dog_name="Bulldog",
                dog_sales=35000,
                trainer_name="Jane Smith",
                commission=3500,
                competition_name=None,
                competition_amount=0,
            ),
            # Example 3: Training + Competition
            Revenue(
                date="2023-01-09",
                revenue_type="Training & Competition",
                dog_name="Beagle",
                dog_sales=0,
                trainer_name="Alice Brown",
                commission=3000,
                competition_name="Speed Contest",
                competition_amount=8000,
            ),
            # Add your other sample entries...
        ]
        db.session.bulk_save_objects(sample_data)
        db.session.commit()



# Helper function to parse date from string
def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "error")
        return None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('service_management')



# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Helper function to send OTP
def send_otp(email):
    try:
        otp = str(random.randint(100000, 999999))
        msg = Message(
            "Your Login OTP", 
            sender=app.config['MAIL_USERNAME'], 
            recipients=[email]
        )
        msg.body = f"Your OTP is: {otp}. It will expire in 10 minutes."
        mail.send(msg)
        print(otp)
        otp_generation_time = datetime.utcnow().isoformat() 
        return otp, otp_generation_time
    
    except Exception as e:
        app.logger.error(f"OTP sending failed: {str(e)}")
        flash('Error sending OTP. Please try again.', 'danger')
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    trainers = TrainerInfo.query.filter_by(status=False).all()  # Fetch all pending trainers
    active_users = User.query.count()  # Count active users
    pending_documents = db.session.query(User).join(TrainerInfo).filter(TrainerInfo.status == False).count()  # Count pending documents
    service_providers = User.query.filter(User.role=='trainer', User.verified==True).count()  # Count service providers
    unverified_trainers = User.query.filter(User.role=='trainer', User.verified==False).count()  # Count unverified trainers
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    unread_count = Notification.query.filter_by(read=False).count() 
    return render_template('admin_dashboard.html', user=current_user, notifications=notifications, unread_count=unread_count, active_users=active_users, pending_documents=pending_documents, service_providers=service_providers, trainers=trainers, unverified_trainers=unverified_trainers)

@app.route('/trainer_dashboard')
@login_required
def trainer_dashboard():
    # Fetch the trainer info based on the current user
    trainer = TrainerInfo.query.filter_by(trainer_id=current_user.id).first()
    
    # Render the template with both user and trainer info
    return render_template('trainer_dashboard.html', user=current_user, trainer=trainer)

@app.route('/customer_dashboard')
@login_required
def customer_dashboard():
    return render_template('customer_dashboard.html', user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and current_user.role == 'customer':
        return redirect(url_for('customer_dashboard'))
    
    elif current_user.is_authenticated and current_user.role == 'trainer':
        return redirect(url_for('trainer_dashboard'))
    
    elif current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        if not name or not email or not password or not confirm_password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        if mobile:
            existing_mobile = User.query.filter_by(mobile_number=mobile).first()
            if existing_mobile:
                flash('Mobile number already exists. Please use a different number.', 'danger')
                return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        otp, otp_generation_time = send_otp(email)
        if otp:
            session['registration_details'] = {
                'name': name,
                'mobile': mobile,
                'email': email,
                'password': hashed_password,
                'role': role
            }
            session['verification_type'] = 'registration'
            session['verification_otp'] = otp
            session['otp_generation_time'] = otp_generation_time
            flash('OTP sent to your email for registration verification', 'info')
            return redirect(url_for('verify_otp'))
        else:
            flash('Failed to send OTP. Please try again.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.role == 'customer':
        return redirect(url_for('customer_dashboard'))
    
    elif current_user.is_authenticated and current_user.role == 'trainer':
        return redirect(url_for('trainer_dashboard'))
    
    elif current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        role = request.form.get('role', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = 'remember' in request.form
        if not email or not password or not role:
            flash('Role, email, and password are required', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email, role=role).first()
        if user and check_password_hash(user.password, password):
            otp, otp_generation_time = send_otp(email)
            session['login_email'] = email
            session['remember_me'] = remember  
            session['verification_type'] = 'login'
            session['verification_otp'] = otp
            session['otp_generation_time'] = otp_generation_time
            flash('OTP sent to your email', 'info')
            return redirect(url_for('verify_otp'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    verification_type = session.get('verification_type')
    if verification_type == 'login':
        if 'login_email' not in session:
            flash('Session expired. Please log in again.', 'warning')
            return redirect(url_for('login'))
        
    elif verification_type == 'registration':
        if 'registration_details' not in session:
            flash('Session expired. Please start registration again.', 'warning')
            return redirect(url_for('register'))
        
    else:
        flash('Invalid verification attempt.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '')
        stored_otp, otp_generation_time = session.get('verification_otp'), session.get('otp_generation_time')  
        otp_generation_time = datetime.fromisoformat(otp_generation_time)
        otp_expiration_time = otp_generation_time + timedelta(minutes=10)
        if datetime.utcnow() > otp_expiration_time:
            flash('OTP has expired.', 'danger')
            return redirect(url_for('resend_otp'))
        
        if entered_otp == stored_otp:
            if verification_type == 'login':
                user = User.query.filter_by(email=session['login_email']).first()
                if user:
                    remember_me = session.get('remember_me', False)
                    user.last_login = datetime.utcnow()
                    login_user(user, remember=remember_me)
                    db.session.commit()
                    session.pop('login_email', None)
                    session.pop('remember_me', None)
                    session.pop('verification_type', None)
                    session.pop('verification_otp', None)
                    flash('Login successful!', 'success')
                    if current_user.role == 'customer':
                        return redirect(url_for('customer_dashboard'))
                    elif current_user.role == 'trainer':
                        return redirect(url_for('trainer_dashboard'))
                    else:
                        return redirect(url_for('admin_dashboard'))
            
            elif verification_type == 'registration':
                reg_details = session['registration_details']
                new_user = User(
                    name=reg_details['name'],
                    mobile_number=reg_details['mobile'],
                    email=reg_details['email'],
                    password=reg_details['password'],
                    role=reg_details['role']
                )
                db.session.add(new_user)
                db.session.commit()
                notification_message = f"New {new_user.role} registered: {new_user.name} ({new_user.email})"
                new_notification = Notification(
                                message=notification_message,
                                user_id=new_user.id  # Link the notification to the user
                            )
                
                db.session.add(new_notification)
                db.session.commit()
                socketio.emit('new_notification', {'message': notification_message, 'created_at': datetime.utcnow().isoformat()})
                try:
                    msg = Message(
                        "Registration Successful!",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[reg_details['email']]
                    )
                    msg.body = f"Dear {reg_details['name']},\n\nThank you for registering on Pet Heaven. Your account has been created successfully.\n\nBest Regards,\nPet Heaven Team"
                    mail.send(msg)
                except Exception as e:
                    app.logger.error(f"Failed to send registration email: {str(e)}")
                    flash('Registration email could not be sent. Please check your inbox later.', 'warning')
                
                session.pop('registration_details', None)
                session.pop('verification_type', None)
                session.pop('verification_otp', None)
                flash('Registration Successful! You can now log in.', 'success')
                return redirect(url_for('login'))
        
        flash('Invalid OTP. Please try again.', 'danger')
    
    return render_template('verify_otp.html')

@app.route('/resend_otp')
def resend_otp():
    verification_type = session.get('verification_type')
    if verification_type == 'login':
        email = session['login_email']
    elif verification_type == 'registration':
        email = session['registration_details']['email']
    else:
        flash('Invalid verification attempt.', 'warning')
        return redirect(url_for('login'))
    
    new_otp, new_otp_generation_time = send_otp(email)
    if new_otp:
        session['verification_otp'] = new_otp
        session['otp_generation_time'] = new_otp_generation_time
        flash('A new OTP has been sent to your email.', 'info')
    else:
        flash('Failed to send OTP. Please try again.', 'danger')
    
    return redirect(url_for('verify_otp'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        if user:
            otp, otp_generation_time = send_otp(email)
            if otp:
                session['password_reset_email'] = email
                session['verification_otp'] = otp
                session['otp_generation_time'] = otp_generation_time
                flash('OTP sent to your email for password reset', 'info')
                return redirect(url_for('reset_password'))
            else:
                flash('Failed to send OTP. Please try again.', 'danger')
        else:
            flash('If the email exists in our system, you will receive a reset link.', 'info')
    
    return render_template('forgot_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'password_reset_email' not in session:
        flash('Password reset session expired. Please start over.', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        otp = request.form.get('otp', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        otp_generation_time = datetime.fromisoformat(session.get('otp_generation_time'))
        if datetime.utcnow() - otp_generation_time > timedelta(minutes=10):
            session.pop('password_reset_email', None)
            session.pop('verification_otp', None)
            session.pop('otp_generation_time', None)
            flash('OTP has expired. Please request a new one.', 'danger')
            return redirect(url_for('forgot_password'))
        
        if otp != session.get('verification_otp'):
            flash('Invalid OTP. Please try again.', 'danger')
            return render_template('reset_password.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset_password.html')
        
        try:
            email = session.get('password_reset_email')
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = generate_password_hash(password, method='pbkdf2:sha256')
                db.session.commit()
                session.pop('password_reset_email', None)
                session.pop('verification_otp', None)
                session.pop('otp_generation_time', None)
                flash('Password updated successfully. Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('User not found. Please try again.', 'danger')
        except Exception as e:
            flash(f"Error updating password: {str(e)}", 'danger')
    
    return render_template('reset_password.html')

from datetime import datetime

@app.route('/submit_trainer_info', methods=['POST'])
def submit_trainer_info():
    form_data = request.form
    try:
        trainer_user = current_user
        if not trainer_user:
            flash('You must be logged in to submit trainer information.', 'danger')
            return redirect(url_for('trainer_validation_form'))
        
        existing_trainer_info = TrainerInfo.query.filter_by(trainer_id=trainer_user.id).first()
        if existing_trainer_info:
            flash('Trainer information already submitted.', 'info')
            return redirect(url_for('trainer_dashboard'))

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

        def secure_filename(filename):
            return filename.replace(' ', '_')

        # Initialize variables
        government_id_path = None
        certification_path = None

        # Handle government ID upload
        government_id_file = request.files.get('government_id')
        if government_id_file and allowed_file(government_id_file.filename):
            government_id_filename = secure_filename(government_id_file.filename)
            government_id_path = os.path.join(app.config['UPLOAD_FOLDER'], government_id_filename)
            try:
                government_id_file.save(government_id_path)
            except Exception as e:
                app.logger.error(f"Error saving government ID: {e}")
                flash("Error saving government ID file.", 'danger')
                return redirect(url_for('trainer_dashboard'))
        else:
            flash('Invalid government ID file.', 'danger')
            return redirect(url_for('trainer_dashboard'))

        # Handle certification file upload
        certification_file = request.files.get('certification')
        if certification_file and allowed_file(certification_file.filename):
            certification_filename = secure_filename(certification_file.filename)
            certification_path = os.path.join(app.config['UPLOAD_FOLDER'], certification_filename)
            try:
                certification_file.save(certification_path)
            except Exception as e:
                app.logger.error(f"Error saving certification: {e}")
                flash("Error saving certification file.", 'danger')
                return redirect(url_for('trainer_dashboard'))
        elif certification_file:
            flash('Invalid certification file.', 'danger')
            return redirect(url_for('trainer_dashboard'))

        # Create new trainer information entry
        trainer_info = TrainerInfo(
            trainer_id=trainer_user.id,
            full_name=form_data.get('full_name'),
            phone_number=form_data.get('phone_number'),
            email=form_data.get('email'),
            website=form_data.get('website'),
            government_id_type=form_data.get('government_id_type'),
            government_id_number=form_data.get('government_id_number'),
            government_id_file=government_id_path,
            certification_name=form_data.get('certification_name'),
            certification_number=form_data.get('certification_number'),
            certification_file=certification_path,  # Use the variable initialized above
            degree=form_data.get('degree'),
            institution_name=form_data.get('institution_name'),
            graduation_year=form_data.get('graduation_year'),
            experience_years=form_data.get('experience_years'),
            species=form_data.get('species'),
            behavioral_issues=form_data.get('behavioral_issues'),
            training_philosophy=form_data.get('training_philosophy'),
            approach_behavioral_issues=form_data.get('approach_behavioral_issues'),
            references=form_data.get('references'),
            reviews=form_data.get('reviews'),
            insurance_coverage=form_data.get('insurance_coverage'),
            insurance_provider=form_data.get('insurance_provider'),
            training_plans=form_data.get('training_plans'),
            progress_monitoring=form_data.get('progress_monitoring'),
            continued_education=form_data.get('continued_education'),
            communication_style=form_data.get('communication_style'),
            ethical_considerations=form_data.get('ethical_considerations'),
            facilities_equipment=form_data.get('facilities_equipment'),
            hours_of_operation=form_data.get('hours_of_operation'),
            session_fees=form_data.get('session_fees'),
            additional_notes=form_data.get('additional_notes'),
        )
        db.session.add(trainer_info)
        db.session.commit()

        notification_message = f"A new trainer has submitted their information: {trainer_user.name} ({trainer_user.email})"
        new_notification = Notification(
            message=notification_message,
            user_id=trainer_user.id
        )
        db.session.add(new_notification)
        db.session.commit()

        socketio.emit('new_notification', {'message': notification_message, 'created_at': datetime.utcnow().isoformat()})
        flash('Trainer information submitted successfully!', 'success')

        try:
            msg = Message(
                'Trainer Information Submission Confirmation',
                sender='companypethaven@gmail.com',
                recipients=[trainer_user.email]
            )
            msg.body = f"Dear {trainer_user.name},\n\nYour trainer information has been successfully submitted. Thank you for providing the details.\n\nBest regards,\nThe Pet Trainer Team"
            mail.send(msg)
            app.logger.info(f"Confirmation email sent to {trainer_user.email}")
        except Exception as e:
            app.logger.error(f"Error sending email: {e}")
            flash(f'Your information was submitted, but there was an issue sending the confirmation email.{e}', 'warning')
        
        return redirect(url_for('trainer_dashboard'))

    except Exception as e:
        app.logger.error(f"Error saving trainer info: {e}")
        flash(f'Error submitting trainer information. Please try again. {e}', 'danger')
        return redirect(url_for('trainer_validation_form'))

@app.route('/trainer_validation_form')
def trainer_validation_form():
    return render_template('trainer_validation_form.html')

# @app.route('/trainer_requests')
# @login_required
# def trainer_requests():
#     trainers = TrainerInfo.query.filter_by(status=False).all()  # Fetch all pending trainers
#     if trainers:
#         return render_template('trainer_requests.html', trainers=trainers)  # Render a list of trainers
#     else:
#         flash('No trainer requests pending.', 'info')
#         return redirect(url_for('admin_dashboard'))  # Redirect to a home or another page



@app.route('/trainer_request/<int:trainer_id>', methods=['GET'])
@login_required
def trainer_request_info(trainer_id):
    trainer = TrainerInfo.query.get(trainer_id)
    if trainer:
        return render_template("trainer_request_info.html", trainer=trainer)  # Render individual trainer request
    else:
        flash('Trainer request not found.', 'danger')
        return redirect(url_for('trainer_requests'))

@app.route('/accept_trainer/<int:trainer_id>', methods=['POST'])
@login_required
def accept_trainer(trainer_id):
    trainer = TrainerInfo.query.get(trainer_id)
    if trainer:
        trainer.status = True  # Set status to True for Verified
        trainer.user.verified = True  # Update the user verification status
        db.session.commit()
        
        # Send email notification
        try:
            msg = Message(
                "Trainer Application Accepted",
                sender=app.config['MAIL_USERNAME'],
                recipients=[trainer.email]  # Assuming the trainer has an email attribute
            )
            msg.body = f"Dear {trainer.full_name},\n\nYour application has been accepted. Welcome to Pet Haven!\n\nBest Regards,\nPet Haven Team"
            mail.send(msg)
            flash('Trainer verified successfully! An email has been sent to the trainer.', 'success')
        except Exception as e:
            app.logger.error(f"Failed to send acceptance email: {str(e)}")
            flash('Trainer verified successfully, but the email could not be sent. Please check your inbox later.', 'warning')
    else:
        flash('Trainer not found.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_trainer/<int:trainer_id>', methods=['POST'])
@login_required
def reject_trainer(trainer_id):
    trainer = TrainerInfo.query.get(trainer_id)
    if trainer:
        trainer.status = False  # Set status to False for Rejected
        db.session.delete(trainer) # Delete the trainer info
        db.session.commit()
        
        # Send email notification
        try:
            msg = Message(
                "Trainer Application Rejected",
                sender=app.config['MAIL_USERNAME'],
                recipients=[trainer.email]  # Assuming the trainer has an email attribute
            )
            msg.body = f"Dear {trainer.full_name},\n\nWe regret to inform you that your application has been rejected. Thank you for your interest in Pet Haven.\n\nBest Regards,\nPet Haven Team"
            mail.send(msg)
            flash('Trainer rejected successfully! An email has been sent to the trainer.', 'success')
        except Exception as e:
            app.logger.error(f"Failed to send rejection email: {str(e)}")
            flash('Trainer rejected successfully, but the email could not be sent. Please check your inbox later.', 'warning')
    else:
        flash('Trainer not found.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route("/trainer/<int:trainer_id>")
@login_required
def trainer_info(trainer_id):
    trainer = TrainerInfo.query.get(trainer_id)
    if trainer:
        return render_template("trainer_info.html", trainer=trainer)
    else:
        return "Trainer not found", 404



@app.route('/admin_dashboard/user_search', methods=['GET', 'POST'])
@login_required  # Ensure only logged-in users can access this route
def user_search():
    users = []
    error_message = None
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            # Try to find users with the given email
            users = User.query.filter_by(email=email).all()
            if not users:
                error_message = "No users found with that email."
        else:
            # **Added validation for empty email field**
            error_message = "Please enter an email to search."

    return render_template('admin/user_search.html', users=users, error_message=error_message)

@app.route('/admin_dashboard/update_user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))  # Redirect to a safe page

    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    new_name = request.form.get('name')
    new_mobile_number = request.form.get('mobile_number')
    updated_fields = []
    # **Only update fields that have changed**
    if new_role and new_role != user.role:
        user.role = new_role
    if new_name and new_name != user.name:
        user.name = new_name
    if new_mobile_number and new_mobile_number != user.mobile_number:
        user.mobile_number = new_mobile_number
    # Commit changes to the database if any updates occurred
    if updated_fields:
        db.session.commit()
        #send email notification
        try:
            msg = Message(
                "Account Details Updated",
                sender=app.config['MAIL_USERNAME'],
                recipients=[user.email]
            )
            msg.body = f"Dear {user.name},\n\nYour account details have been updated by an admin. If you did not make these changes, please contact support.\n\nBest Regards,\nPet Haven Team"
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send account update email: {str(e)}")
            flash('Account details updated successfully, but the email could not be sent. Please check your inbox later.', 'warning')

        flash('User details updated successfully!', 'success')
    else:
        flash('No changes detected.', 'warning')

    flash('User details updated successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/mark_notifications_read', methods=['POST'])
@login_required
def mark_notifications_read():
    # Mark all notifications as read for the current user
    Notification.query.filter_by(read=False).update({'read': True})
    db.session.commit()
    return '', 204  # No content response

@app.route('/admin_dashboard/all_notifications', methods=['GET'])
@login_required
def all_notifications():
    if current_user.role != 'admin':
        return {'error': 'Unauthorized'}, 403  # Return an error if not admin

    # Get the offset from the query parameters
    offset = int(request.args.get('offset', 0))  # Default to 0 if not provided
    # Fetch notifications starting from the offset
    notifications = Notification.query.order_by(Notification.created_at.desc()).offset(offset).limit(3).all()
    # Return notifications in JSON format
    return {
        'notifications': [
            {
                'message': notification.message,
                'created_at': notification.created_at.isoformat()  # Convert datetime to ISO format
            }
            for notification in notifications
    ]}

@app.route('/notification/<int:notification_id>')
@login_required
def notification_details(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    # Mark the notification as read
    notification.read = True
    db.session.commit()
    # Extract the email from the notification message
    email = notification.message.split(" (")[1].rstrip(")")  # Assuming the message format is "New user registered: Name (email@example.com)"
    # Fetch user details from the database using the email
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User  not found.', 'danger')
        return redirect(url_for('dashboard'))

    # Prepare registration details
    registration_details = {
        'name': user.name,
        'email': user.email,
        'mobile': user.mobile_number,
        'role': user.role,
    }
    return render_template('admin/notification_details.html', notification=notification, registration_details=registration_details)

# SocketIO event handler for notifications
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


####Team 2####
# User view (list of dogs)
@app.route('/d')
def user_view():
    dogs = Dog.query.all()
    breed_filter = request.args.get('breed', '')
    age_filter = request.args.get('age', '')
    price_filter = request.args.get('price', '')

    # Apply filters
    filtered_dogs = [dog for dog in dogs if
                     (breed_filter.lower() in dog.breed.lower() if breed_filter else True) and
                     (age_filter == '<5' and dog.age < 5 or
                      age_filter == '5-10' and 5 <= dog.age <= 10 or
                      age_filter == '10-15' and 10 <= dog.age <= 15 or
                      age_filter == '15-20' and 15 <= dog.age <= 20 or
                      age_filter == '>20' and dog.age > 20 or
                      not age_filter) and
                     (price_filter == '<10000' and dog.price < 10000 or
                      price_filter == '10000-20000' and 10000 <= dog.price <= 20000 or
                      price_filter == '20000-30000' and 20000 <= dog.price <= 30000 or
                      price_filter == '30000-40000' and 30000 <= dog.price <= 40000 or
                      price_filter == '>40000' and dog.price > 40000 or
                      not price_filter)]

    return render_template('index.html', dogs=filtered_dogs, admin=False)

# Admin view (list of dogs)
@app.route('/admin')
def admin_view():
    dogs = Dog.query.all()
    return render_template('index.html', dogs=dogs, admin=True)

# Add dog
@app.route('/add_dog', methods=['GET', 'POST'])
def add_dog():
    if request.method == 'POST':
        breed = request.form['breed']
        age = request.form['age']
        price = request.form['price']
        traits = request.form['traits']
        vaccination_details = request.form['vaccination_details']
        health_info = request.form['health_info']
        grooming_info = request.form['grooming_info']
        trainability = request.form['trainability']
        height = request.form['height']
        weight = request.form['weight']
        image = request.form['image']

        new_dog = Dog(breed=breed, age=age, price=price, image=image, traits=traits,
                        vaccination_details=vaccination_details, health_info=health_info,
                        grooming_info=grooming_info, trainability=trainability, height=height, weight=weight)
            
        db.session.add(new_dog)
        db.session.commit()

        return redirect(url_for('admin_view'))  

    return render_template('add.html')

# Remove dog
@app.route('/remove_dog/<int:id>', methods=['POST'])
def remove_dog(id):
    dog = Dog.query.get(id)
    if dog:
        db.session.delete(dog)
        db.session.commit()
    return redirect(url_for('admin_view'))

# Edit dog details
@app.route('/edit_dog/<int:id>', methods=['GET', 'POST'])
def edit_dog(id):
    dog = Dog.query.get(id)

    if not dog:
        return redirect(url_for('admin_view'))

    if request.method == 'POST':
        dog.breed = request.form['breed']
        dog.age = request.form['age']
        dog.price = request.form['price']
        dog.vaccination_details = request.form['vaccination_details']
        dog.health_info = request.form['health_info']
        dog.grooming_info = request.form['grooming_info']
        dog.trainability = request.form['trainability']
        dog.height = request.form['height']
        dog.weight = request.form['weight']
        dog.image = request.form['image']
        dog.traits = request.form['traits']

        db.session.commit()
        return redirect(url_for('admin_view'))

    return render_template('edit.html', dog=dog)

# Dog details for user view
@app.route('/dog/<int:id>')
def user_dog_description(id):
    dog = Dog.query.get(id)
    if not dog:
        return "Dog not found", 404
    return render_template('dogDescription.html', dog=dog, admin=False)

# Dog details for admin view
@app.route('/admin/dog/<int:id>')
def admin_dog_description(id):
    dog = Dog.query.get(id)
    if not dog:
        return "Dog not found", 404
    return render_template('dogDescription.html', dog=dog, admin=True)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    try:
        # Parse JSON data
        data = request.get_json()
        print("Received data:", data)  # Debugging
        user_id = current_user.id
        print("User ID:", user_id)  # Debugging

        # Extract data
        service_id = data.get('service_id')
        dog_id = data.get('dog_id')
        trainer_id = data.get('trainer_id')
        service_id3 = data.get('service_id3')  # For service
        timeslot_id = data.get('timeslot_id')
        booking_date = data.get('booking_date')

        # Validate input data
        if not any([dog_id, service_id, trainer_id, service_id3]):
            print("Error: Missing required data")
            return jsonify({'message': 'Invalid request: Missing required data'}), 400

        new_cart_item = None

        # Handle dog addition
        if dog_id:
            dog = Dog.query.get_or_404(dog_id)
            existing_item = Cart.query.filter_by(user_id=user_id, dog_id=dog_id, confirm_booking=False).first()

            if existing_item:
                print("Dog already in cart")
                return jsonify({'message': 'Dog is already in your cart'}), 409

            new_cart_item = Cart(
                user_id=user_id,
                dog_id=dog_id,
                breed=dog.breed,
                age=dog.age,
                price=dog.price,
                image=dog.image
            )

        # Handle competition/event addition
        elif service_id:
            competition = Competition.query.get_or_404(service_id)
            
            # Check if the event is already in the cart for the user and is not confirmed
            existing_item = Cart.query.filter_by(user_id=user_id, service_id=service_id, confirm_booking=False).first()

            if existing_item:
                print("Event already in cart")
                return jsonify({'message': 'Event already in cart'}), 409

            new_cart_item = Cart(
                user_id=user_id,
                service_id=service_id,
                title=competition.title,
                date=competition.date,
                time=competition.time,
                price=competition.price
            )

        # Handle service booking addition
        elif trainer_id and service_id3:
            if not all([timeslot_id, booking_date]):
                print("Missing timeslot or booking date")
                return jsonify({'message': 'Missing timeslot or booking date'}), 400

            trainer = Trainer.query.get_or_404(trainer_id)
            service = Service.query.get_or_404(service_id3)

            existing_item = Cart.query.filter_by(
                user_id=user_id,
                trainer_id=trainer_id,
                service_id3=service_id3,
                booking_date=datetime.strptime(booking_date, '%Y-%m-%d').date(),
                timeslot_id=timeslot_id,
                confirm_booking=False
            ).first()

            if existing_item:
                print("Service booking already in cart")
                return jsonify({'message': 'Service booking already in cart'}), 409

            new_cart_item = Cart(
                user_id=user_id,
                trainer_id=trainer_id,
                service_id3=service_id3,
                timeslot_id=timeslot_id,
                booking_date=datetime.strptime(booking_date, '%Y-%m-%d').date(),
                tname=trainer.tname,  # Corrected to trainer.tname
                service_name=service.service_name,
                price=service.cost  # Corrected to service.cost
            )

        # Add new cart item if valid
        if new_cart_item:
            db.session.add(new_cart_item)
            db.session.commit()
            print("Item added to cart:", new_cart_item)  # Debugging

        # Calculate updated cart details
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        total_quantity = sum(item.quantity for item in cart_items if hasattr(item, 'quantity'))
        total_price = sum(item.price * (item.quantity if hasattr(item, 'quantity') else 1) for item in cart_items)

        return jsonify({
            'message': 'Dog added to cart successfully',
            'total_quantity': total_quantity,
            'total_price': total_price
        }), 201

    except Exception as e:
        print("Error:", str(e))  # Debugging
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

    
@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id , confirm_booking=False).all()
    
    total_quantity = sum(item.quantity for item in cart_items)
    total_price = sum(item.price * item.quantity for item in cart_items)
    
    return render_template('cart.html', 
                            cart_items=cart_items,
                            total_quantity=total_quantity,
                            total_price=total_price)

# Remove dog from cart
@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
@login_required  # Ensure only the cart owner can remove items
def remove_from_cart(cart_id):
    # Get the cart item and ensure it belongs to the current user
    cart_item = Cart.query.filter_by(id=cart_id, user_id=current_user.id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from cart successfully'}), 200
    return jsonify({'message': 'Error removing item from cart'}), 400


# Update quantity in the cart
@app.route('/update_quantity', methods=['POST'])
@login_required  # Ensure the current user is authenticated
def update_quantity():
    data = request.get_json()
    dog_id = data['dog_id']
    action = data['action']

    # Get the cart item and ensure it belongs to the current user
    cart_item = Cart.query.filter_by(dog_id=dog_id, user_id=current_user.id).first()
    if cart_item:
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1

        db.session.commit()

        # Recalculate totals for the current user's cart
        user_cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        total_quantity = sum(item.quantity for item in user_cart_items)
        total_price = sum(item.price * item.quantity for item in user_cart_items)

        return jsonify({
            'message': 'Quantity updated successfully',
            'new_quantity': cart_item.quantity,
            'total_quantity': total_quantity,
            'total_price': total_price
        }), 200

    return jsonify({'message': 'Error updating quantity'}), 400

@app.route('/add_to_wishlist', methods=['POST'])
@login_required  # Ensure only authenticated users can access
def add_to_wishlist():
    data = request.get_json()
    dog_id = data['dog_id']

    # Check if the dog is already in the current user's wishlist
    existing_wishlist_item = Wishlist.query.filter_by(dog_id=dog_id, user_id=current_user.id).first()
    dog = Dog.query.get(dog_id)

    if existing_wishlist_item:
        return jsonify({
            'message': 'Dog already in the wishlist'
        }), 200

    # Add new dog to the user's wishlist
    new_wishlist_item = Wishlist(
        user_id=current_user.id,
        dog_id=dog_id,
        breed=dog.breed,
        age=dog.age,
        price=dog.price,
        image=dog.image
    )
    db.session.add(new_wishlist_item)
    db.session.commit()

    return jsonify({
        'message': 'Dog added to wishlist successfully'
    }), 200

@app.route('/add_to_cart_from_wishlist', methods=['POST'])
@login_required  # Ensure only authenticated users can access
def add_to_cart_from_wishlist():
    data = request.get_json()
    dog_id = data.get('dog_id')

    if not dog_id:
        return jsonify({'message': 'Dog ID is missing'}), 400

    # Check if the dog exists
    dog = Dog.query.get(dog_id)
    if not dog:
        return jsonify({'message': 'Dog not found'}), 404

    # Check if the dog is already in the current user's cart
    existing_cart_item = Cart.query.filter_by(dog_id=dog_id, user_id=current_user.id).first()

    if existing_cart_item:
        return jsonify({'message': 'Dog already in the cart'}), 200

    # Add new dog to the user's cart
    new_cart_item = Cart(
        user_id=current_user.id,
        dog_id=dog_id,
        breed=dog.breed,
        age=dog.age,
        price=dog.price,
        image=dog.image
    )
    db.session.add(new_cart_item)
    db.session.commit()

    return jsonify({'message': 'Dog added to cart successfully'}), 200

# Remove a dog from the wishlist
@app.route('/remove_from_wishlist/<int:wishlist_id>', methods=['POST'])
@login_required  # Ensure only the owner can remove items
def remove_from_wishlist(wishlist_id):
    # Fetch the wishlist item and ensure it belongs to the current user
    wishlist_item = Wishlist.query.filter_by(id=wishlist_id, user_id=current_user.id).first()
    if wishlist_item:
        try:
            db.session.delete(wishlist_item)
            db.session.commit()
            return jsonify({'message': 'Dog removed from wishlist successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error removing item from wishlist'}), 400
    return jsonify({'message': 'Dog not found in wishlist'}), 404


# View the user's wishlist
@app.route('/wishlist')
@login_required  # Ensure only authenticated users can view their wishlist
def wishlist():
    # Fetch wishlist items for the current user
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    total_quantity = len(wishlist_items)  # Total number of items in the wishlist
    total_price = sum(item.price for item in wishlist_items)  # Total price of all items

    return render_template(
        'wishlist.html',
        wishlist_items=wishlist_items,
        total_quantity=total_quantity,
        total_price=total_price
    )

#checkout
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Fetch cart items for the current user
    cart_items = Cart.query.filter_by(user_id=current_user.id,confirm_booking=False).all()

    # Check if the cart is empty
    if not cart_items:
        flash('Your cart is empty. Please add items to proceed to checkout.', 'warning')
        return redirect('/cart')  # Redirect to the cart page

    dog_items = [item for item in cart_items if item.breed]  # Assuming 'breed' exists for dogs
    event_items = [item for item in cart_items if item.title]  # Assuming 'title' exists for events
    service_items = [item for item in cart_items if item.tname]  # Assuming 'service_name' exists for services
        # Calculate total quantity and price
    total_quantity = sum(item.quantity for item in cart_items if hasattr(item, 'quantity'))
    total_price = sum(item.price * (item.quantity if hasattr(item, 'quantity') else 1) for item in cart_items)
    # Calculate cart totals
    cart_data = {
        'total_quantity': total_quantity,
        'total_price': total_price,
        'cart_items': dog_items + event_items+ service_items
    }

    if request.method == 'POST':
        # Handle POST-specific logic (e.g., proceed to payment)
        return render_template('checkout.html', cart_data=cart_data)

    # For a GET request, render the checkout page with cart_data
    return render_template('checkout.html', cart_data=cart_data)


@app.route('/process-checkout', methods=['POST'])
@login_required
def process_checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id , confirm_booking=False).all()

    if not cart_items:
        flash('Your cart is empty. Please add items before checking out.', )
        return redirect('/cart')

    # Clear the cart after checkout
    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    flash('Checkout completed successfully!', 'success')
    return redirect('/cart')  # Redirect to the cart or another success page



@app.route('/payments')
def payments():
    return render_template('payments.html')

@app.route('/thank-you', methods=['POST', 'GET'])
def thank_you():
    # payment_method = request.form.get('payment_method')
    # Optionally process payment details here
    return render_template('thankyou.html')

@app.route('/submit_payment', methods=['POST'])
def submit_payment():
    # Retrieve the user_id from the form data
    try:
        # Fetch the cart items for the given user_id
        cart_items = Cart.query.filter_by(user_id=current_user.id , confirm_booking=False).all()
        print(f"Cart items fetched for user_id {current_user.id}: {cart_items}")  # Debug: Log cart items

        if not cart_items:
            print("Cart is empty.")  # Debug
            return "No items in the cart to confirm", 400
                # Initialize summaries and total price
        dog_summary = {}
        trainer_summary = {}
        competition_summary = {}
        total_price = 0

        # Update the confirm_booking column for all cart items of the user
        for item in cart_items:
            print(f"Updating item {item.id} to confirm booking.")  # Debug: Log item updates
            item.confirm_booking = True  # Set confirm_booking to True

            # Add to summaries for email
            if item.dog:
                dog_summary[item.dog.breed] = dog_summary.get(item.dog.breed, 0) + item.price
            if item.trainer:
                trainer_summary[item.trainer.tname] = trainer_summary.get(item.trainer.tname, 0) + item.price
            if item.competition:
                competition_summary[item.competition.title] = competition_summary.get(item.competition.title, 0) + item.price
            
            total_price += item.price

            # Transfer the cart item to the Revenue table
            revenue_entry = Revenue(
                date=str(datetime.now().date()), 
                dog_name=item.dog.breed if item.dog else None,
                dog_sales=item.price if item.dog_id else 0,
                trainer_name=item.trainer.tname if item.trainer else None,
                commission=item.price * 0.2 if item.trainer else 0,  # Example: 20% commission
                competition_name=item.competition.title if item.competition else None,
                competition_amount=item.price if item.service_id else 0,
            )
            db.session.add(revenue_entry)  # Add the revenue entry to the session

        # Commit the changes to the database
        db.session.commit()
        print("Booking confirmed and database updated.")  # Debug: Log success
        
        # Send the confirmation email to the user
            # Prepare the email content
        email_content = "Dear {},\n\nThank you for your purchase on Pet Heaven! Here is the summary of your order:\n".format(current_user.name)
        if dog_summary:
            email_content += "\nDogs Purchased:\n"
            for dog, price in dog_summary.items():
                email_content += f"- {dog}: ₹{price}\n"

        if trainer_summary:
            email_content += "\nTrainers Booked:\n"
            for trainer, price in trainer_summary.items():
                email_content += f"- {trainer}: ₹{price}\n"

        if competition_summary:
            email_content += "\nCompetitions Registered:\n"
            for competition, price in competition_summary.items():
                email_content += f"- {competition}: ₹{price}\n"

        email_content += f"\nTotal Price: ₹{total_price}\n"
        email_content += "We appreciate your business!\n\nBest Regards,\nTeam Pet Heaven"

            # Send Confirmation Email
        try:
            msg = Message(
                subject="Booking Confirmation from Pet Heaven",
                sender=app.config['MAIL_USERNAME'],  # Ensure this is set in your config
                recipients=[current_user.email]
            )
            msg.body = email_content
            mail.send(msg)
            print("Confirmation email sent successfully.")  # Debugging log

        except Exception as e:
            app.logger.error(f"Failed to send confirmation email: {str(e)}")
            flash('Booking email could not be sent. Please check your inbox later.', 'warning')
            
            # Return a success response with redirect URL
        return jsonify({
            "success": True, 
            "redirect": url_for('thank_you')
        }), 200

    except Exception as e:
        # Handle any errors and rollback if needed
        db.session.rollback()
        print(f"An error occurred: {str(e)}")  # Debug: Log error
        return f"An error occurred: {str(e)}", 500


#team 4 routes
@app.route('/c')
def home4():
    services = Competition.query.all()
    return render_template('index4.html', services=services)

@app.route('/admin4')
def admin4():
    services = Competition.query.all()
    return render_template('admin4.html', services=services)
def validate_service_data(title, date, time, description):
    errors = []
    
    if not title or len(title.strip()) < 3:
        errors.append("Title must be at least 3 characters long")
        
    try:
        datetime.strptime(date, '%d-%m-%Y')
    except ValueError:
        errors.append("Date must be in DD-MM-YYYY format")
        
    try:
        datetime.strptime(time.lower(), '%I:%M %p')
    except ValueError:
        errors.append("Time must be in HH:MM am/pm format (e.g., 10:00 am)")
        
    if not description or len(description.strip()) < 10:
        errors.append("Description must be at least 10 characters long")
        
    return errors

@app.route('/admin4/events')
@login_required
def admin_events():
    try:
        # Query competitions and count of paid registrations
        competition_stats = db.session.query(
            Competition.title,
            db.func.count(Cart.id).label('registration_count')
        ).join(
            Cart,
            Competition.id == Cart.service_id
        ).filter(
            Cart.confirm_booking == True
        ).group_by(
            Competition.title
        ).all()
        
        # Convert to dictionary for template
        competitions_dict = {
            comp.title: comp.registration_count 
            for comp in competition_stats
        }
        
        return render_template('admin_events.html', competitions_dict=competitions_dict)
    except Exception as e:
        logger.error(f"Error fetching competition statistics: {e}")
        flash("Error loading competition statistics", "danger")
        return redirect(url_for('admin4'))
    
    

@app.route('/admin4/add_competition', methods=['GET', 'POST'])
def add_competition():
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('competition_name')
            date = request.form.get('date')
            time = request.form.get('time')
            description = request.form.get('description')
            price = request.form.get('price')

            # Validate required fields
            if not all([title, date, time, description, price]):
                flash("All fields are required!", "danger")
                return render_template('add_competition.html')

            # Validate price to ensure it's a positive number
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be a positive value")
            except ValueError as e:
                flash(f"Invalid price: {e}", "danger")
                return render_template('add_competition.html')

            # Format date to match the existing format (assuming input is YYYY-MM-DD)
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d-%m-%Y')
            except ValueError as e:
                flash("Invalid date format!", "danger")
                return render_template('add_competition.html')

            # Format time to match the existing format (assuming input is HH:MM)
            try:
                time_obj = datetime.strptime(time, '%H:%M')
                formatted_time = time_obj.strftime('%I:%M %p').lower()
            except ValueError as e:
                flash("Invalid time format!", "danger")
                return render_template('add_competition.html')

            # Create new competition
            new_competition = Competition(
                title=title,
                date=formatted_date,
                time=formatted_time,
                description=description,
                price=price  # Add price to the competition
            )

            # Add to database with error handling
            try:
                db.session.add(new_competition)
                db.session.commit()
                flash("Competition added successfully!", "success")
                return redirect(url_for('admin4'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error while adding competition: {e}")
                flash(f"Database error: {str(e)}", "danger")
                return render_template('add_competition.html')

        except Exception as e:
            logger.error(f"Error during competition addition: {e}")
            flash(f"Error: {str(e)}", "danger")
            return render_template('add_competition.html')

    # GET request
    return render_template('add_competition.html')


@app.route('/admin4/delete_competition/<int:service_id>', methods=['POST'])
def delete_competition(service_id):
    try:
        service = Competition.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting service: {str(e)}")
        flash('Failed to delete event', 'danger')
    
    return redirect(url_for('admin4'))


@app.route('/admin4/edit_competition4/<int:service_id>', methods=['GET', 'POST'])
def edit_competition4(service_id):
    try:
        service = Competition.query.get_or_404(service_id)
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('competition_name')
            date = request.form.get('date')
            time = request.form.get('time')
            description = request.form.get('description')
            capacity = request.form.get('capacity')
            price = request.form.get('price')  # Get the price from the form

            # Validate form data
            errors = validate_service_data(title, date, time, description)
            
            if price:
                try:
                    price = float(price)
                    if price <= 0:
                        errors.append("Price must be a positive value")
                except ValueError:
                    errors.append("Price must be a valid number")
            
            if capacity:
                try:
                    capacity = int(capacity)
                    if capacity < service.registered_count:
                        errors.append("New capacity cannot be less than current registrations")
                    elif capacity <= 0:
                        errors.append("Capacity must be greater than 0")
                except ValueError:
                    errors.append("Capacity must be a valid number")

            if errors:
                for error in errors:
                    flash(error, "danger")
                return render_template('edit4.html', service=service)

            # Update service details
            service.title = title
            service.date = date
            service.time = time
            service.description = description
            if capacity:
                service.capacity = capacity
            if price:
                service.price = price  # Update price in the service

            try:
                db.session.commit()
                flash("Competition updated successfully!", "success")
                return redirect(url_for('admin4'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error while updating competition: {e}")
                flash("Error updating competition", "danger")
                return render_template('edit4.html', service=service)

    except Exception as e:
        logger.error(f"Error in edit_competition route: {e}")
        flash("An error occurred while processing your request", "danger")
        return redirect(url_for('admin4'))

    # GET request
    return render_template('edit4.html', service=service)

@app.route('/myevents4')
def myevents4():
    try:
        # Get all confirmed competition payments for the current user from Revenue table
        paid_competitions = db.session.query(Competition.title).join(
        Cart,
        Competition.id == Cart.service_id
        ).filter(
            Cart.user_id == current_user.id,
            Cart.confirm_booking == True,
        ).distinct().all()
    
        # Extract competition names into a list
        competition_list = [comp[0] for comp in paid_competitions]
        
        return render_template('myevents4.html', competition_list=competition_list)
    except Exception as e:
        logger.error(f"Error fetching registration: {e}")
        flash("Error loading registration", "danger")
        return redirect(url_for('home4'))

@app.route('/schedule4')
def schedule4():
    competitions = Competition.query.order_by(Competition.date).all()
    # Render the template and pass the competitions
    return render_template('schedule4.html', competitions=competitions)


def get_current_time():
    now_utc = datetime.now(timezone.utc)
    # IST is UTC + 5:30
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = now_utc + ist_offset
    return now_ist.date(), now_ist.time()

# Add a new route to handle payment completion
@app.route('/complete_payment', methods=['POST'])
def complete_payment():
    current_date, current_time = get_current_time()
    try:
        registration_data = session.get('registration_data')
        user_details = session.get('user_details')
        if not registration_data or not user_details:
            flash("No registration or user details data found!", "danger")
            return redirect(url_for('home4'))
        # Create new user with the stored registration data
        new_user = DogDetails(
            name=registration_data['name'],
            breed=registration_data['breed'],
            age=registration_data['age'],
            event=registration_data['event']
        )
        db.session.add(new_user)
        db.session.commit()
        # Create user details record
        new_user_details = UserDetails(
            user_id=new_user.id,
            name=user_details['name'],
            email=user_details['email'],
            phone=user_details['phone'],
            address=user_details['address'],
            created_date=current_date,
            created_time=current_time
        )
        
        db.session.add(new_user_details)
        db.session.commit()
        
        
        # Clear the session data
        session.pop('registration_data', None)
        session.pop('user_details', None)
        flash("Registration and payment completed successfully!", "success")
        return redirect(url_for('index4'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during payment completion: {e}")
        flash("Error completing registration", "danger")
        return redirect(url_for('payments4'))
    

@app.route('/register4', methods=['GET', 'POST'])
def register4():
    service_id = request.args.get('service_id')
    service = Competition.query.get(service_id)

    if not service:
        flash("Service not found!", "danger")
        return redirect(url_for('home4'))

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            breed = request.form.get('breed')
            age = request.form.get('age')
            event = service.title

            if not all([name, breed, age]):
                flash("All fields are required!", "danger")
                return render_template('register4.html', service=service)

            try:
                age = int(age)
                if age < 0:
                    raise ValueError("Age must be positive")
            except ValueError as e:
                flash(f"Invalid age: {str(e)}", "danger")
                return render_template('register4.html', service=service)

            # Store registration data in session instead of database
            session['registration_data'] = {
                'name': name,
                'breed': breed,
                'age': age,
                'event': event
            }
            
            return redirect(url_for('details4'))

        except Exception as e:
            logger.error(f"Error during registration process: {e}")
            flash(f"Error: {str(e)}", "danger")
            return render_template('register4.html', service=service)

    return render_template('register4.html', service=service)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
#team 3#

# Routes for user 
@app.route('/services')
def list_services():
    services = Service.query.all()
    return render_template('services3.html', services=services)

@app.route('/tservices')
def tlist_services():
    services = Service.query.all()
    return render_template('tservices.html', services=services)

@app.route('/services/<int:service_id>')
def trainers_by_service(service_id):
    service = Service.query.get_or_404(service_id)
    trainers = Trainer.query.filter_by(service_id=service_id).all()
    return render_template('trainers.html', service=service, trainers=trainers)

@app.route('/tservices/<int:service_id>')
def trainers_by_service2(service_id):
    service = Service.query.get_or_404(service_id)
    trainers = Trainer.query.filter_by(service_id=service_id).all()
    return render_template('ttrainers.html', service=service, trainers=trainers)

@app.route('/services/<int:service_id>/appointments', methods=['GET'])
def direct_appointment(service_id):
    trainer_id = request.args.get('trainer_id', type=int)
    if trainer_id is None:
        return "Trainer ID is required", 400  # Return an error if trainer_id is not provided

    trainer = Trainer.query.get_or_404(trainer_id)
    service = Service.query.get_or_404(service_id)
    slots = TimeSlot.query.all()
    today = datetime.now().date()
    max_date = today.replace(year=today.year + 1)  # Allow bookings up to 1 year in advance
    return render_template(
        'appointment.html', 
        trainer=trainer, 
        service=service, 
        slots=slots, 
        service_id=service_id, 
        today=today, 
        max_date=max_date
    )

@app.route('/tservices/<int:service_id>/appointments', methods=['GET'])
def tdirect_appointment(service_id):
    trainer_id = request.args.get('trainer_id', type=int)
    if trainer_id is None:
        return "Trainer ID is required", 400  # Return an error if trainer_id is not provided

    trainer = Trainer.query.get_or_404(trainer_id)
    service = Service.query.get_or_404(service_id)
    slots = TimeSlot.query.all()
    today = datetime.now().date()
    max_date = today.replace(year=today.year + 1)  # Allow bookings up to 1 year in advance
    return render_template(
        'tappointment.html', 
        trainer=trainer, 
        service=service, 
        slots=slots, 
        service_id=service_id, 
        today=today, 
        max_date=max_date
    )


@app.route('/get-available-slots', methods=['POST'])
def get_available_slots():
    data = request.get_json()
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    trainer_id = data['trainer_id']
    
    # Get all time slots
    all_slots = TimeSlot.query.all()
    
    # Get booked slot IDs for the selected date and trainer
    booked_slots = db.session.query(TimeSlot.id).join(Booking).filter(
        Booking.booking_date == date,
        Booking.trainer_id == trainer_id
    ).all()
    booked_slot_ids = [slot[0] for slot in booked_slots]  # Extract IDs from tuples
    
    # Prepare available slots
    available_slots = [
        {'id': slot.id, 'time': slot.time_slot}
        for slot in all_slots
        if slot.id not in booked_slot_ids
    ]
    
    # Prepare booked slots
    booked_slots_data = [
        {'id': slot_id, 'time': TimeSlot.query.get(slot_id).time_slot}
        for slot_id in booked_slot_ids
    ]
    
    return jsonify({
        'availableSlots': available_slots,
        'bookedSlots': booked_slots_data
    })


@app.route('/services/<int:service_id>/appointments/confirm-appointment', methods=['POST'])
def confirm_appointment(service_id):
    trainer_id = request.form.get('trainer_id', type=int)
    date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
    timeslot_id = request.form.get('time_slot', type=int)
    
    # Check if slot is still available
    existing_booking = Booking.query.filter_by(
        trainer_id=trainer_id,
        booking_date=date,
        timeslot_id=timeslot_id
    ).first()
    
    if existing_booking:
        flash('Sorry, this slot has just been booked. Please select another time.', 'error')
        return redirect(url_for('direct_appointment', trainer_id=trainer_id, service_id=service_id))
    
    # Create new booking
    booking = Booking(
        trainer_id=trainer_id,
        service_id=service_id,
        booking_date=date,
        timeslot_id=timeslot_id
    )
    
    try:    
        db.session.add(booking)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
    except:
        db.session.rollback()
        flash('An error occurred while booking. Please try again.', 'error')
        return redirect(url_for('direct_appointment', trainer_id=trainer_id, service_id=service_id))

    # Send confirmation email
    # try:
    #     msg = Message(
    #         "Appointment Confirmed",
    #         sender=app.config['MAIL_USERNAME'],
    #         recipients=[date['email']]
    #     )
    #     msg.body = f"Dear {date['name']},\n\nThank you for booking an appointment on Pet Heaven. Your booking has been confirmed successfully.\n\nBest Regards,\nPet Heaven Team"
    #     mail.send(msg)
    # except Exception as e:
    #     app.logger.error(f"Failed to send Booking Confirmation email: {str(e)}")
    #     flash('Booking Confirmation email could not be sent. Please check your inbox later.', 'warning')
    
    return redirect(url_for('booking_confirmation', booking_id=booking.id))

SERVICE_PRICES = {
    'Grooming': 1500,
    'Relaxation Therapy': 1350,
    'Health Care': 2000
}

@app.route('/booking-confirmation/<int:booking_id>', methods=['GET'])
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    price = SERVICE_PRICES.get(booking.service.service_name, 0)
    return render_template('booking_confirmation.html', booking=booking, price=price)

@app.route('/create-order', methods=['POST'])
def create_order():
    data = request.get_json()  # Get the price from the request body
    price = data.get('price', 0)  # Default to 0 if price is not provided

    # Convert price to subunits (paise for INR)
    amount_in_paise = int(price * 100)


@app.route('/payment-success', methods=['POST'])
def payment_success():
    data = request.json
    msg = Message("Payment Confirmation", recipients=[data['customer_email']])
    msg.body = f"Dear {data['customer_name']},\n\nYour payment of {data['amount']/100} INR was successful!\nThank you for choosing Dog Spa.\n\nBest Regards,\nDog Spa Team"
    mail.send(msg)

    return jsonify({"message": "Notification sent!"}), 200

@app.route('/payment-failure', methods=['POST'])
def payment_failure():
    data = request.json
    msg = Message("Payment Failure", recipients=[data['customer_email']])
    msg.body = f"Dear {data['customer_name']},\n\nYour payment of {data['amount']/100} INR failed. Please try again.\n\nBest Regards,\nDog Spa Team"
    mail.send(msg)

    return jsonify({"message": "Notification sent!"}), 200

@app.route('/add_services', methods=['GET', 'POST'])
def add_services():
    if request.method == 'POST':
        try:
            # Get form data
            service_name = request.form.get('service_name')
            duration = request.form.get('duration')
            cost = request.form.get('cost')
            description = request.form.get('description')

            # Validate required fields
            if not all([service_name, duration, cost, description]):
                flash("All fields are required!", "error")
                return render_template('add_services.html')

            # Validate service name
            if not service_name.replace(' ', '').isalpha() or not (3 <= len(service_name) <= 50):
                flash("Service name must be 3-50 characters and contain only letters and spaces", "error")
                return render_template('add_services.html')

            # Validate duration
            try:
                duration = int(duration)
                if not (1 <= duration <= 480):
                    flash("Duration must be between 1 and 480 minutes", "error")
                    return render_template('add_services.html')
            except ValueError:
                flash("Duration must be a valid number", "error")
                return render_template('add_services.html')

            # Validate cost
            try:
                cost = float(cost)
                if cost < 0:
                    flash("Cost cannot be negative", "error")
                    return render_template('add_services.html')
            except ValueError:
                flash("Cost must be a valid number", "error")
                return render_template('add_services.html')

            # Validate description length
            if not (10 <= len(description) <= 200):
                flash("Description must be between 10 and 200 characters", "error")
                return render_template('add_services.html')

            # Create new service
            new_service = Service(
                service_name=service_name,
                duration=duration,
                cost=cost,
                description=description
            )

            # Add to database with error handling
            try:
                db.session.add(new_service)
                db.session.commit()
                flash("Service added successfully!", "success") 
                return redirect(url_for('admin_services'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error while adding service: {e}")
                flash("Error adding service to database", "error")
                return render_template('add_services.html')

        except Exception as e:
            logger.error(f"Error during service addition: {e}")
            flash("An unexpected error occurred", "error")
            return render_template('add_services.html')

    # GET request
    return render_template('add_services.html')

@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    try:
        service = Service.query.get_or_404(service_id)
        
        if request.method == 'POST':
            # Get form data
            service_name = request.form.get('service_name')
            duration = request.form.get('duration')
            cost = request.form.get('cost')
            description = request.form.get('description')

            # Validate required fields
            if not all([service_name, duration, cost, description]):
                flash("All fields are required!", "error")
                return render_template('edit_service.html', service=service)

            # Validate service name
            if not service_name.replace(' ', '').isalpha() or not (3 <= len(service_name) <= 50):
                flash("Service name must be 3-50 characters and contain only letters and spaces", "error")
                return render_template('edit_service.html', service=service)

            # Validate duration
            try:
                duration = int(duration)
                if not (1 <= duration <= 480):
                    flash("Duration must be between 1 and 480 minutes", "error")
                    return render_template('edit_service.html', service=service)
            except ValueError:
                flash("Duration must be a valid number", "error")
                return render_template('edit_service.html', service=service)

            # Validate cost
            try:
                cost = float(cost)
                if cost < 0:
                    flash("Cost cannot be negative", "error")
                    return render_template('edit_service.html', service=service)
            except ValueError:
                flash("Cost must be a valid number", "error")
                return render_template('edit_service.html', service=service)

            # Validate description length
            if not (10 <= len(description) <= 200):
                flash("Description must be between 10 and 200 characters", "error")
                return render_template('edit_service.html', service=service)

            # Update service details
            try:
                service.service_name = service_name
                service.duration = duration
                service.cost = cost
                service.description = description

                db.session.commit()
                flash("Service updated successfully!", "success")
                return redirect(url_for('admin_services'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error while updating service: {e}")
                flash("Error updating service", "error")
                return render_template('edit_service.html', service=service)

    except Exception as e:
        logger.error(f"Error in edit_service route: {e}")
        flash("An error occurred while processing your request", "error")
        return redirect(url_for('admin3'))

    # GET request
    return render_template('edit_service.html', service=service)

@app.route('/delete_service/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    try:
        service = Service.query.get_or_404(service_id)
        
        # Delete all trainers associated with the service
        Trainer.query.filter_by(service_id=service_id).delete()
        
        # Delete the service
        db.session.delete(service)
        db.session.commit()
        flash('Service and associated trainers deleted successfully!', 'success')
        return redirect(url_for('admin_services'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting service: {str(e)}")
        flash('Failed to delete service', 'error')
    return redirect(url_for('admin3'))

@app.route('/admin_services')
def admin_services():
    services = Service.query.all()
    return render_template('admin_services.html', services=services)

@app.route('/admin_services/<int:service_id>/admin_trainer')
def admin_trainer(service_id):
    service = Service.query.get_or_404(service_id)
    return render_template('admin_trainer.html', service=service)

@app.route('/admin_services/<int:service_id>/add_trainer', methods=['GET', 'POST'])
def add_trainer(service_id):
    try:
        service = Service.query.get_or_404(service_id)

        if request.method == 'POST':
            trainer_name = request.form.get('trainer-name')
            trainer_number = request.form.get('trainer-number')
            experience = request.form.get('experience')
            rating = request.form.get('rating')
            description = request.form.get('description')
            profile_pic = request.files.get('profile-pic')

            # Validate required fields
            if not all([trainer_name, trainer_number, experience, rating, description, profile_pic]):
                flash("All fields are required!", "error")
                return render_template('add_trainer.html', service=service)

            # Validate trainer name
            if not trainer_name.replace(' ', '').isalpha() or not (3 <= len(trainer_name) <= 50):
                flash("Trainer name must be 3-50 characters and contain only letters and spaces", "error")
                return render_template('add_trainer.html', service=service)

            # Handle profile picture upload
            if profile_pic:
                filename = secure_filename(profile_pic.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_{filename}"

                try:
                    profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                    profile_pic_path = f"../static/images/{unique_filename}"
                except Exception as e:
                    logger.error(f"Error saving profile picture: {e}")
                    flash("Error saving profile picture", "error")
                    return render_template('add_trainer.html', service=service)

            # Create new trainer
            new_trainer = Trainer(
                service_id=service_id,
                tname=trainer_name,
                mobile_number=trainer_number,
                experience=f"{experience} years",
                rating=float(rating),
                description=description,
                profile_pic=profile_pic_path,
            )

            try:
                db.session.add(new_trainer)
                db.session.commit()
                flash("Trainer added successfully!", "success")
                return redirect(url_for('admin_trainer', service_id=service_id))

            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error while adding trainer: {e}")
                flash("Error adding trainer to database", "error")
                return render_template('add_trainer.html', service=service)

        # GET request
        return render_template('add_trainer.html', service=service)

    except Exception as e:
        logger.error(f"Error in add_trainer route: {e}")
        flash("An unexpected error occurred", "error")
        return redirect(url_for('admin_trainer', service_id=service_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/trainers/<int:trainer_id>/edit', methods=['GET', 'POST'])
def edit_trainer(trainer_id):
    try:
        # Fetch the trainer by ID
        trainer = Trainer.query.get_or_404(trainer_id)
        service_id = trainer.service_id

        if request.method == 'POST':
            trainer_name = request.form.get('name')
            experience = request.form.get('experience')
            rating = request.form.get('rating')
            description = request.form.get('description')
            file = request.files.get('profile_pic')

            # Validate required fields
            if not all([trainer_name, experience, rating, description]):
                flash("All fields except profile picture are required!", "error")
                return render_template('edit_trainer.html', trainer=trainer)

            # Validate trainer name
            if not trainer_name.replace(' ', '').isalpha() or not (3 <= len(trainer_name) <= 50):
                flash("Trainer name must be 3-50 characters and contain only letters and spaces", "error")
                return render_template('edit_trainer.html', trainer=trainer)

            # Handle file upload if present
            if file and allowed_file(file.filename):
                # Secure the filename and save the file
                filename = secure_filename(file.filename)
                
                # Define the directory where images will be stored (static/images/)
                file_path = os.path.join('static', 'images', filename)
                
                # Save the file to the static/images/ directory
                file.save(file_path)
                
                # Hardcode the path to be stored in the database
                trainer.profile_pic = f'images/{filename}'  # Save relative path

            # Update other trainer details
            trainer.tname = trainer_name
            trainer.experience = experience
            trainer.rating = float(rating)
            trainer.description = description

            try:
                # Save changes to the database
                db.session.commit()
                flash("Trainer details updated successfully!", "success")
                return redirect(url_for('admin_trainer', service_id=service_id))

            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error while updating trainer: {e}")
                flash("Error updating trainer details", "error")
                return render_template('edit_trainer.html', trainer=trainer)

            try:
                msg = Message(
                        "Details Successfully Updated!",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[reg_details['email']]
                    )
                msg.body = f"Dear {reg_details['name']},\n\nYour account details has been updated successfully.\n\nBest Regards,\nPet Heaven Team"
                mail.send(msg)
                
            except Exception as e:
                app.logger.error(f"Failed to send Update details confirmation email: {str(e)}")
                flash('Account details update email could not be sent. Please check your inbox later.', 'warning')

        # GET request: Render the edit form with the trainer's details
        return render_template('edit_trainer.html', trainer=trainer)

    except Exception as e:
        logger.error(f"Error in edit_trainer route: {e}")
        flash("An unexpected error occurred", "error")
        return redirect(url_for('admin_trainer', service_id=service_id))


@app.route('/admin_services/<int:service_id>/trainer/<int:trainer_id>/delete', methods=['POST'])
def delete_trainer(service_id, trainer_id):
    try:
        trainer = Trainer.query.get_or_404(trainer_id)
        # Delete the profile picture file if it exists
        if trainer.profile_pic:
            try:
                image_path = trainer.profile_pic.replace('../static/', '')
                profile_pic_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
                if os.path.exists(profile_pic_path):
                    os.remove(profile_pic_path)
            except Exception as e:
                logger.error(f"Error deleting profile picture: {e}")

        # Delete from database
        db.session.delete(trainer)
        db.session.commit()
        flash("Trainer deleted successfully!", "success")
        return redirect(url_for('admin_trainer', service_id=service_id))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting trainer: {e}")
        flash(f"Error deleting trainer: {str(e)}", "error")
        return redirect(url_for('admin_trainer', service_id=service_id))


#team 5

@app.route('/r')
def index():
    return render_template('index5.html')

@app.route('/api/revenue')
def get_revenue():
    # Calculate total revenue (sum of all three types)
    total_revenue = (
        db.session.query(
            func.coalesce(func.sum(Revenue.dog_sales), 0) +
            func.coalesce(func.sum(Revenue.commission), 0) +
            func.coalesce(func.sum(Revenue.competition_amount), 0)
        ).scalar()
    )

    # Calculate total commission
    total_commission = db.session.query(func.coalesce(func.sum(Revenue.commission), 0)).scalar()

    # Bookings by type
    bookings_by_type = {
        "Dog Sales": db.session.query(func.count(Revenue.id)).filter(Revenue.dog_sales > 0).scalar(),
        "Dog Training": db.session.query(func.count(Revenue.id)).filter(Revenue.commission > 0).scalar(),
        "Competition": db.session.query(func.count(Revenue.id)).filter(Revenue.competition_amount > 0).scalar()
    }

    # Total bookings
    total_bookings = sum(bookings_by_type.values())

    # Revenue breakdown by type
    revenue_breakdown = {
        "Dog Sales": db.session.query(func.coalesce(func.sum(Revenue.dog_sales), 0)).scalar(),
        "Dog Training": db.session.query(func.coalesce(func.sum(Revenue.commission), 0)).scalar(),
        "Competition Earnings": db.session.query(func.coalesce(func.sum(Revenue.competition_amount), 0)).scalar()
    }

    # Monthly revenue trends
    monthly_trends = dict(db.session.query(
        func.substr(Revenue.date, 1, 7),  # Extract YYYY-MM from the date
        func.coalesce(func.sum(Revenue.dog_sales), 0) +
        func.coalesce(func.sum(Revenue.commission), 0) +
        func.coalesce(func.sum(Revenue.competition_amount), 0)
    ).group_by(func.substr(Revenue.date, 1, 7))
    .order_by(func.substr(Revenue.date, 1, 7)).all())

    # Yearly revenue trends
    yearly_trends = dict(db.session.query(
        func.substr(Revenue.date, 1, 4),  # Extract YYYY from the date
        func.coalesce(func.sum(Revenue.dog_sales), 0) +
        func.coalesce(func.sum(Revenue.commission), 0) +
        func.coalesce(func.sum(Revenue.competition_amount), 0)
    ).group_by(func.substr(Revenue.date, 1, 4))
    .order_by(func.substr(Revenue.date, 1, 4)).all())

    # Trainer performance
    trainer_performance = dict(db.session.query(
        Revenue.trainer_name,
        func.coalesce(func.sum(Revenue.dog_sales), 0) +
        func.coalesce(func.sum(Revenue.commission), 0) +
        func.coalesce(func.sum(Revenue.competition_amount), 0)
    ).filter(Revenue.trainer_name.isnot(None))
    .group_by(Revenue.trainer_name)
    .order_by(
        (func.coalesce(func.sum(Revenue.dog_sales), 0) +
            func.coalesce(func.sum(Revenue.commission), 0) +
            func.coalesce(func.sum(Revenue.competition_amount), 0)).desc()
    ).all())

    # Competition revenue breakdown
    competition_breakdown = dict(db.session.query(
        Revenue.competition_name,
        func.coalesce(func.sum(Revenue.competition_amount), 0)
    ).filter(Revenue.competition_name.isnot(None))
    .group_by(Revenue.competition_name)
    .order_by(func.sum(Revenue.competition_amount).desc()).all())

    # Dog revenue breakdown
    dog_revenue = dict(db.session.query(
        Revenue.dog_name,
        func.coalesce(func.sum(Revenue.dog_sales), 0)
    ).filter(Revenue.dog_name.isnot(None))
    .group_by(Revenue.dog_name)
    .order_by(func.sum(Revenue.dog_sales).desc()).all())

    # Prepare the response data
    data = {
        'total_revenue': total_revenue,
        'total_commission': total_commission,
        'net_profit': total_revenue - total_commission,
        'total_bookings': total_bookings,
        'bookings_by_type': bookings_by_type,
        'revenue_breakdown': revenue_breakdown,
        'monthly_trends': monthly_trends,
        'yearly_trends': yearly_trends,
        'trainer_performance': trainer_performance,
        'competition_breakdown': competition_breakdown,
        'dog_revenue': dog_revenue
    }

    return jsonify(data)

@app.route('/trainer_dashboard/edit_details', methods=['GET', 'POST'])
@login_required
def edit_details():
    # Fetch trainer details for the current user
    trainer = Trainer.query.filter_by(mobile_number=current_user.mobile_number).first()
    trainer_info = TrainerInfo.query.filter_by(trainer_id=current_user.id).first()  # Fetch TrainerInfo based on current_user.id

    if not trainer:
        flash('Trainer not found!', 'danger')
        return redirect(url_for('trainer_dashboard'))

    if request.method == 'POST':
        # Fetch new values from the form
        new_name = request.form.get('tname')
        new_mobile_number = request.form.get('mobile_number')

        # Check if the mobile number is changed
        if new_mobile_number != current_user.mobile_number:
            # Ensure the new mobile number is not already taken in Trainer, User, and TrainerInfo tables
            existing_trainer = Trainer.query.filter_by(mobile_number=new_mobile_number).first()
            existing_user = User.query.filter_by(mobile_number=new_mobile_number).first()
            existing_trainer_info = TrainerInfo.query.filter_by(phone_number=new_mobile_number).first()

            if existing_trainer or existing_user or existing_trainer_info:
                flash('This mobile number is already in use.', 'danger')
                return redirect(url_for('edit_details'))

            # Update all tables where mobile number exists
            Trainer.query.filter_by(mobile_number=current_user.mobile_number).update({"mobile_number": new_mobile_number})
            User.query.filter_by(mobile_number=current_user.mobile_number).update({"mobile_number": new_mobile_number})
            
            # Fetch and update the TrainerInfo instance
            if trainer_info:
                trainer_info.phone_number = new_mobile_number
                trainer_info.trainer_id = current_user.id  # Ensure this is linked properly

        # Handle profile picture upload
        profile_pic = request.files.get('profile_pic')  # Assuming 'profile_pic' is the name of the file input field
        profile_pic_path = trainer.profile_pic  # Default to current profile picture path

        if profile_pic:
            filename = secure_filename(profile_pic.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"

            # Make sure the upload folder exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

            profile_pic_path = f"../static/images/{unique_filename}"  # Assuming the folder is static/images

        # Update Trainer table
        trainer.tname = new_name
        trainer.experience = request.form.get('experience')
        trainer.rating = request.form.get('rating')
        trainer.description = request.form.get('description')
        trainer.profile_pic = profile_pic_path  # Update the profile picture path
        # Update User table
        current_user.name = new_name
        # Update TrainerInfo table
        if trainer_info:
            trainer_info.full_name = new_name

        try:
            db.session.commit()
            flash('Trainer details updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while updating trainer details: {str(e)}', 'danger')

        return redirect(url_for('trainer_dashboard'))

    return render_template('edit_details.html', trainer=trainer)


@app.route('/request_edit/<int:trainer_id>', methods=['POST'])
@login_required
def request_edit(trainer_id):
    trainer = TrainerInfo.query.get(trainer_id)
    if trainer:
        trainer.status = True  # Set status to False for Verified
        db.session.commit()
        
    return redirect(url_for('edit_details'))


@app.route('/trainer_dashboard/session-details')
@login_required
def session_details():
    # Ensure the user is a trainer
    trainer = Trainer.query.filter_by(mobile_number=current_user.mobile_number).first()
    if not trainer:
        flash('Trainer not found!', 'danger')
        return redirect(url_for('trainer_dashboard'))

    # Fetch session details for the trainer
    sessions = (
        db.session.query(Booking, Service, TimeSlot)
        .join(Service, Booking.service_id == Service.id)
        .join(TimeSlot, Booking.timeslot_id == TimeSlot.id)
        .filter(Booking.trainer_id == trainer.id)
        .all()
    )

    return render_template('session_details.html', sessions=sessions, trainer=trainer)


@app.route('/add_admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        number = request.form['number']
        password = request.form['password']

        if not all([name, email, number, password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_admin'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('add_admin'))
        
        existing_user = User.query.filter_by(mobile_number=number).first()
        if existing_user:
            flash('Mobile number already exists. Please use a different number.', 'danger')
            return redirect(url_for('add_admin'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_admin = User(
            name=name,
            email=email,
            mobile_number=number,
            password=hashed_password,
            role='admin'
        )
        db.session.add(new_admin)
        db.session.commit()

        # Send email to the new admin
        try:
            msg = Message(
                "Admin Account Created",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = f"Dear {name},\n\nYour admin account has been created successfully.\n Your account email:- {email} \n pasword={password}.\n\nBest Regards,\nPet Haven Team"
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send Admin Account email: {str(e)}")
            flash('Admin Account email could not be sent. Please check your inbox later.', 'warning')

        # Notify admin about the new admin addition
        notification_message = f"New admin added: {new_admin.name} ({new_admin.email})"
        new_notification = Notification(
            message=notification_message,
            user_id=new_admin.id
        )
        db.session.add(new_notification)
        db.session.commit()
        socketio.emit('new_notification', {'message': notification_message, 'created_at': datetime.utcnow().isoformat()})

        flash('New admin added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/add_admin.html')

# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)