import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from models import db, User, Patient, Visit, Procedure
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY', 'dev-key-change-in-production')

# Use absolute path for database in the main folder
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'clinic.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create database tables and default users
with app.app_context():
    db.create_all()

    # Create default users if they don't exist
    if not User.query.filter_by(username='assistant').first():
        assistant = User(username='assistant',
                         password='assistant123', role='assistant')
        db.session.add(assistant)

    if not User.query.filter_by(username='doctor').first():
        doctor = User(username='doctor', password='doctor123', role='doctor')
        db.session.add(doctor)

    db.session.commit()
    print("Database created successfully at:",
          os.path.join(basedir, 'clinic.db'))
    print("Default users created: assistant/assistant123, doctor/doctor123")

# ==================== LOGIN REQUIRED DECORATOR ====================


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'doctor':
            flash('Doctor access required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def assistant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        if session.get('role') not in ['assistant', 'doctor']:
            flash('Access denied', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== WHATSAPP MESSAGING (COMING SOON) ====================
# Uncomment this section when you have Twilio WhatsApp approved
#
# from twilio.rest import Client
#
# TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
# TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
# TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')
#
# def send_whatsapp(to_number, message):
#     try:
#         to_number = ''.join(filter(str.isdigit, to_number))
#         if not to_number.startswith('92'):
#             to_number = '92' + to_number[-10:] if len(to_number) >= 10 else to_number
#         client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#         message = client.messages.create(
#             body=message,
#             from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
#             to=f'whatsapp:+{to_number}'
#         )
#         return True, message.sid
#     except Exception as e:
#         print(f"WhatsApp error: {e}")
#         return False, str(e)

# ==================== AUTHENTICATION ROUTES ====================


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(
            username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            flash(f'Welcome back, {username}!', 'success')

            if user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

# ==================== ASSISTANT / COMMON ROUTES ====================


@app.route('/')
@login_required
def index():
    """Home page - Dashboard for Assistant"""
    # If doctor, redirect to doctor dashboard
    if session.get('role') == 'doctor':
        return redirect(url_for('doctor_dashboard'))

    today = datetime.utcnow().date()

    # Get today's visits
    today_visits = Visit.query.filter(
        db.func.date(Visit.visit_date) == today
    ).count()

    # Get today's revenue
    today_revenue = db.session.query(db.func.sum(Visit.total_paid)).filter(
        db.func.date(Visit.visit_date) == today
    ).scalar() or 0

    # Get total patients
    total_patients = Patient.query.count()

    return render_template('index.html',
                           today_visits=today_visits,
                           today_revenue=today_revenue,
                           total_patients=total_patients,
                           role=session.get('role'))


@app.route('/patients')
@login_required
def patients():
    """List all patients"""
    all_patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('patients.html', patients=all_patients, role=session.get('role'))


@app.route('/patient/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """Add new patient"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')

        patient = Patient(name=name, phone=phone, email=email)
        db.session.add(patient)
        db.session.commit()

        flash('Patient added successfully!', 'success')
        return redirect(url_for('patients'))

    return render_template('patient_form.html')


@app.route('/patient/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    """View patient details and history"""
    patient = Patient.query.get_or_404(patient_id)
    return render_template('patient_detail.html', patient=patient, role=session.get('role'))


@app.route('/patient/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """Edit patient information - Both assistant and doctor can edit"""
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        patient.name = request.form.get('name')
        patient.phone = request.form.get('phone')
        patient.email = request.form.get('email')
        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('patient_detail', patient_id=patient.id))

    return render_template('patient_edit.html', patient=patient)


@app.route('/patient/<int:patient_id>/delete', methods=['POST'])
@doctor_required
def delete_patient(patient_id):
    """Delete a patient - DOCTOR ONLY"""
    patient = Patient.query.get_or_404(patient_id)
    name = patient.name
    db.session.delete(patient)
    db.session.commit()
    flash(f'Patient "{name}" deleted successfully!', 'success')
    return redirect(url_for('patients'))


@app.route('/checkin/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def checkin(patient_id):
    """Check in a patient"""
    patient = Patient.query.get_or_404(patient_id)

    if request.method == 'POST':
        slip_fee = float(request.form.get('slip_fee', 0))

        visit = Visit(
            patient_id=patient.id,
            slip_fee=slip_fee,
            total_paid=slip_fee
        )
        db.session.add(visit)
        db.session.commit()

        flash(f'✅ Check-in complete! Visit ID: {visit.id}', 'success')

        return redirect(url_for('visit_detail', visit_id=visit.id))

    return render_template('checkin.html', patient=patient)


@app.route('/visit/<int:visit_id>')
@login_required
def visit_detail(visit_id):
    """View visit details and add procedures"""
    visit = Visit.query.get_or_404(visit_id)
    return render_template('visit_detail.html', visit=visit, role=session.get('role'))


@app.route('/visit/<int:visit_id>/add_procedure', methods=['POST'])
@login_required
def add_procedure(visit_id):
    """Add a procedure to a visit"""
    visit = Visit.query.get_or_404(visit_id)

    procedure_name = request.form.get('procedure_name')
    procedure_cost = float(request.form.get('procedure_cost', 0))
    paid_amount = float(request.form.get('paid_amount', 0))
    notes = request.form.get('notes', '')

    procedure = Procedure(
        visit_id=visit.id,
        procedure_name=procedure_name,
        procedure_cost=procedure_cost,
        paid_amount=paid_amount,
        notes=notes
    )
    db.session.add(procedure)

    visit.total_paid += paid_amount
    db.session.commit()

    flash('Procedure added successfully!', 'success')
    return redirect(url_for('visit_detail', visit_id=visit.id))


@app.route('/procedure/<int:procedure_id>/edit', methods=['GET', 'POST'])
@doctor_required
def edit_procedure(procedure_id):
    """Edit procedure - DOCTOR ONLY"""
    procedure = Procedure.query.get_or_404(procedure_id)
    visit_id = procedure.visit_id

    if request.method == 'POST':
        old_paid = procedure.paid_amount

        procedure.procedure_name = request.form.get('procedure_name')
        procedure.procedure_cost = float(request.form.get('procedure_cost', 0))
        procedure.paid_amount = float(request.form.get('paid_amount', 0))
        procedure.notes = request.form.get('notes', '')

        # Update visit total
        visit = Visit.query.get(visit_id)
        visit.total_paid = visit.total_paid - old_paid + procedure.paid_amount

        db.session.commit()
        flash('Procedure updated successfully!', 'success')
        return redirect(url_for('visit_detail', visit_id=visit_id))

    return render_template('edit_procedure.html', procedure=procedure)


@app.route('/procedure/<int:procedure_id>/delete', methods=['POST'])
@doctor_required
def delete_procedure(procedure_id):
    """Delete procedure - DOCTOR ONLY"""
    procedure = Procedure.query.get_or_404(procedure_id)
    visit_id = procedure.visit_id
    visit = Visit.query.get(visit_id)

    # Subtract from total paid
    visit.total_paid -= procedure.paid_amount

    db.session.delete(procedure)
    db.session.commit()

    flash('Procedure deleted successfully!', 'success')
    return redirect(url_for('visit_detail', visit_id=visit_id))


@app.route('/visit/<int:visit_id>/print')
@login_required
def print_slip(visit_id):
    """Generate printable prescription slip"""
    visit = Visit.query.get_or_404(visit_id)
    return render_template('print_slip.html', visit=visit)


@app.route('/reports')
@doctor_required
def reports():
    """View financial reports - DOCTOR ONLY"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)

    visits = Visit.query.filter(Visit.visit_date >= start_date).all()

    total_revenue = sum(visit.total_paid for visit in visits)
    total_visits = len(visits)
    avg_per_visit = total_revenue / total_visits if total_visits > 0 else 0

    # Daily breakdown
    daily_data = defaultdict(
        lambda: {'visits': 0, 'slip_total': 0, 'procedure_total': 0, 'total': 0})

    for visit in visits:
        date_str = visit.visit_date.strftime('%Y-%m-%d')
        daily_data[date_str]['visits'] += 1
        daily_data[date_str]['slip_total'] += visit.slip_fee
        daily_data[date_str]['procedure_total'] += (
            visit.total_paid - visit.slip_fee)
        daily_data[date_str]['total'] += visit.total_paid

    daily_breakdown = [
        {'date': date,
         'visits': data['visits'],
         'slip_total': data['slip_total'],
         'procedure_total': data['procedure_total'],
         'total': data['total']}
        for date, data in sorted(daily_data.items(), reverse=True)
    ]

    return render_template('reports.html',
                           days=days,
                           total_revenue=total_revenue,
                           total_visits=total_visits,
                           avg_per_visit=avg_per_visit,
                           visits=visits,
                           daily_breakdown=daily_breakdown,
                           role=session.get('role'))


# ==================== DOCTOR MOBILE ROUTES ====================

@app.route('/doctor')
@doctor_required
def doctor_dashboard():
    """Doctor's mobile-friendly dashboard"""
    today = datetime.utcnow().date()

    # Today's visits with patient and procedure details
    today_visits_list = Visit.query.filter(
        db.func.date(Visit.visit_date) == today
    ).order_by(Visit.visit_date.desc()).all()

    today_visits = len(today_visits_list)

    # Today's revenue
    today_revenue = db.session.query(db.func.sum(Visit.total_paid)).filter(
        db.func.date(Visit.visit_date) == today
    ).scalar() or 0

    # Total patients
    total_patients = Patient.query.count()

    # Month revenue
    month_start = datetime.utcnow().replace(day=1)
    month_revenue = db.session.query(db.func.sum(Visit.total_paid)).filter(
        Visit.visit_date >= month_start
    ).scalar() or 0

    return render_template('doctor_dashboard.html',
                           today_visits=today_visits,
                           today_visits_list=today_visits_list,
                           today_revenue=today_revenue,
                           total_patients=total_patients,
                           month_revenue=month_revenue,
                           role='doctor')


@app.route('/doctor/patients')
@doctor_required
def doctor_patients():
    """Doctor's patient list (read-only with edit options)"""
    all_patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('doctor_patients.html', patients=all_patients)


@app.route('/doctor/visit/<int:visit_id>')
@doctor_required
def doctor_visit_detail(visit_id):
    """Doctor's full visit detail with edit/delete options"""
    visit = Visit.query.get_or_404(visit_id)
    return render_template('doctor_visit_detail.html', visit=visit)


# ==================== RUN SERVER ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
