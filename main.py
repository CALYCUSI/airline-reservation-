from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Aim
# The idea is to develop a web-based airline reservation application using the Flask Microframework.
# Users can login which will give them access to seeing their existing reservations if any and the capability to modify existing reservations or delete a reservation.
# Users can also create new reservations to travel to a particular destination, at a particular date, their classes, if it is a domestic or international flight.
# I intend to use the popular Python micro-framework, Flask for the web application. 
# I will utilize Sqlite as the database for storing and retrieving reservation information. 
# Flask is responsible for the server/backend. For the User Interface, HTML, CSS and Javascript will be used.

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservations.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination = db.Column(db.String(150), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    flight_class = db.Column(db.String(50), nullable=False)
    flight_type = db.Column(db.String(50), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    reservations = Reservation.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', reservations=reservations)

@app.route('/create_reservation', methods=['GET', 'POST'])
def create_reservation():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        destination = request.form['destination']
        travel_date = datetime.strptime(request.form['travel_date'], '%Y-%m-%d')
        flight_class = request.form['flight_class']
        flight_type = request.form['flight_type']
        new_reservation = Reservation(user_id=session['user_id'], destination=destination,
                                      travel_date=travel_date, flight_class=flight_class,
                                      flight_type=flight_type)
        db.session.add(new_reservation)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('create_reservation.html')

@app.route('/modify_reservation/<int:reservation_id>', methods=['GET', 'POST'])
def modify_reservation(reservation_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    reservation = Reservation.query.get_or_404(reservation_id)
    if request.method == 'POST':
        reservation.destination = request.form['destination']
        reservation.travel_date = datetime.strptime(request.form['travel_date'], '%Y-%m-%d')
        reservation.flight_class = request.form['flight_class']
        reservation.flight_type = request.form['flight_type']
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('modify_reservation.html', reservation=reservation)

@app.route('/delete_reservation/<int:reservation_id>')
def delete_reservation(reservation_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    reservation = Reservation.query.get_or_404(reservation_id)
    db.session.delete(reservation)
    db.session.commit()
    return redirect(url_for('dashboard'))

from werkzeug.security import generate_password_hash, check_password_hash

'''@app.route('/register', methods=['GET', 'POST'])'''

def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')
        with connect_db() as db:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

''' @app.route('/login', methods=['GET', 'POST'])'''
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with connect_db() as db:
            user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user and check_password_hash(user[2], password):
                session['logged_in'] = True
                session['user_id'] = user[0]
                return redirect(url_for('index'))
        return "Invalid credentials"
    return render_template('login.html')

'''@app.route('/logout')'''
def logout():
    session.clear()
    return redirect(url_for('login'))


'''@app.route('/reserve', methods=['GET', 'POST'])
@login_required'''
def reserve():
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        destination = request.form['destination']
        departure_date = request.form['departure_date']
        flight_class = request.form['class']
        user_id = session['user_id']
        with connect_db() as db:
            db.execute("INSERT INTO reservations (user_id, flight_number, destination, departure_date, class) VALUES (?, ?, ?, ?, ?)",
                       (user_id, flight_number, destination, departure_date, flight_class))
            db.commit()
        return redirect(url_for('reservations'))
    return render_template('search_flights.html')

'''@app.route('/reservations')
@login_required'''
def reservations():
    user_id = session['user_id']
    with connect_db() as db:
        reservations = db.execute("SELECT * FROM reservations WHERE user_id = ?", (user_id,)).fetchall()
    return render_template('reservations.html', reservations=reservations)

'''@app.route('/cancel/<int:id>')
@login_required'''
def cancel(id):
    with connect_db() as db:
        db.execute("DELETE FROM reservations WHERE id = ?", (id,))
        db.commit()
    return redirect(url_for('reservations'))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
