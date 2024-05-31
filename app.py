import sqlite3 as sql
from flask import Flask, render_template, request, redirect, url_for,jsonify , session, flash
import sqlite3
from voiture import Voiture
from manager import Manager
from client import Client
from administrateur import Administrator
import time
import random
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/photo'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

app.secret_key = 'your_secret_key'


def fetch_cars_from_database():
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voiture")
    cars = cursor.fetchall()
    conn.close()
    return cars

def fetch_cars_from_database_filtered(min_price=None, max_price=None, brand=None, category=None, search=None, availability=None):
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()

    sql_query = "SELECT * FROM voiture WHERE 1=1"
    params = []

    if min_price:
        sql_query += " AND prix >= ?"
        params.append(min_price)
    if max_price:
        sql_query += " AND prix <= ?"
        params.append(max_price)
    if brand:
        sql_query += " AND marque = ?"
        params.append(brand)
    if category:
        sql_query += " AND categorie = ?"
        params.append(category)
    if search:
        sql_query += " AND (marque LIKE ? OR modele LIKE ?)"
        params.append('%' + search + '%')
        params.append('%' + search + '%')
    if availability:
        if availability == "Disponible":
            sql_query += " AND disponible = 1"  # Assuming '1' represents available
        elif availability == "Non disponible":
            sql_query += " AND disponible = 0"  # Assuming '0' represents not available

    cursor.execute(sql_query, params)
    cars = cursor.fetchall()
    
    conn.close()
    return cars
@app.route("/cars")
def get_cars():
    cars = fetch_cars_from_database()
    cars_list = []
    for car in cars:
        car_dict = {
            "id": car[0],
            "marque": car[1],
            "modele": car[2],
            "immatriculation": car[3],
            "categorie": car[4],
            "prix": car[5],
            "disponibilite": car[6],
            "image_url": car[7]
        }
        cars_list.append(car_dict)
    return jsonify(cars_list)


@app.route("/gallery")
def  gallery():
    return render_template('gallery.html')
@app.route("/")
def index():
        # Connect to the SQLite database
    conn = sqlite3.connect('loc.db')
    cursor = conn.cursor()

    # Execute a query to fetch car data (adjust query based on your schema)
    cursor.execute("SELECT * FROM voiture ORDER BY RANDOM() LIMIT 3")
    cars = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Pass car data to the template
    return render_template('index.html', cars=cars) 


@app.route("/car_detail/<int:car_id>")
def car_detail(car_id):
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voiture WHERE id_voiture = ?", (car_id,))
    car_data = cursor.fetchone()
    conn.close()
    if car_data:
        car_obj = Voiture(*car_data)
        return render_template("detail.html", car=car_obj)
    else:
        return "Car not found", 404


@app.route("/reservation_form/<int:car_id>")
def reservation_form(car_id):
    return render_template("reservation_form.html", car_id=car_id)



@app.route("/submit_reservation/<int:car_id>", methods=["POST"])
def submit_reservation(car_id):
    if request.method == "POST":
        # Extract the form data
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        prenom = request.form['prenom']

        # Check if client with the provided email exists
        conn = sqlite3.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM client WHERE email = ?", (email,))
        client = cursor.fetchone()  # Fetch one matching client or None
        
        if not client:
            # Insert the new client into the database
            cursor.execute("INSERT INTO client (nom, prenom, email, telephone) VALUES (?, ?, ?, ?)",
                           (name, prenom, email, phone))
            conn.commit()
            # Retrieve the client ID of the newly inserted client
            client_id = cursor.lastrowid
        else:
            # Existing client found, retrieve the client ID
            client_id = client[0]

        # Check if the car is already reserved (disponibilite = 'Non disponible')
        cursor.execute("SELECT disponibilite FROM voiture WHERE id_voiture = ?", (car_id,))
        disponibilite = cursor.fetchone()

    # Update voiture availability to 'Non disponible'
        cursor.execute(
            "UPDATE voiture SET disponibilite='Non disponible' WHERE id_voiture=?", (car_id,)
        )
        # Insert the reservation into the database
        cursor.execute("INSERT INTO reservation (id_client, id_voiture, status) VALUES (?, ?, ?)",
                       (client_id, car_id, 'Pending'))
        conn.commit()
        conn.close()

        # Redirect to a confirmation page
        return redirect(url_for("reservation_confirmation"))

    # If the request method is not POST, return an error
    return render_template("error.html", message="Invalid request method.")

    
@app.route("/reservation_confirmation")
def reservation_confirmation():
    return render_template("reservation_confirmation.html")

@app.route("/cars_html")
def display_cars_html():
    # Get filter parameters from the URL query string
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    brand = request.args.get('brand')
    category = request.args.get('category')
    search = request.args.get('search')
    availability = request.args.get('availability')

    # Fetch cars from the database with applied filters
    cars = fetch_cars_from_database_filtered(min_price, max_price, brand, category, search, availability)

    # Shuffle the list of cars randomly
    random.shuffle(cars)

    # Render the HTML template with the shuffled list of cars
    return render_template("cars.html", cars=cars)
@app.route("/home")
def home():
    if 'email' in session:
        # Connect to the database
        conn = sqlite3.connect('loc.db')
        cursor = conn.cursor()

        # Fetch the last car added
        cursor.execute("SELECT * FROM voiture ORDER BY id_voiture DESC LIMIT 1")
        last_car_added = cursor.fetchone()

        # Fetch the last car reserved
        cursor.execute("SELECT voiture.*, reservation.id_client FROM voiture JOIN reservation ON voiture.id_voiture = reservation.id_voiture ORDER BY reservation.id_reservation DESC LIMIT 1")
        last_car_reserved = cursor.fetchone()

        # Fetch the last reservation
        cursor.execute("SELECT * FROM reservation ORDER BY id_reservation DESC LIMIT 1")
        last_reservation = cursor.fetchone()

        # Count the number of cars
        cursor.execute("SELECT COUNT(*) FROM voiture")
        num_cars = cursor.fetchone()[0]

        # Count the number of clients (distinct clients with reservations)
        cursor.execute("SELECT COUNT(DISTINCT id_client) FROM reservation")
        num_clients = cursor.fetchone()[0]

        # Calculate the total revenue (sum of prices for accepted reservations)
        cursor.execute("SELECT SUM(voiture.prix) FROM reservation JOIN voiture ON reservation.id_voiture = voiture.id_voiture WHERE reservation.status = 'Accepted'")
        total_revenue = cursor.fetchone()[0] or 0

        # Close the database connection
        conn.close()

        # Render the home page with the fetched data
        return render_template("home.html", 
                               last_car_added=last_car_added, 
                               last_car_reserved=last_car_reserved, 
                               last_reservation=last_reservation,
                               num_cars=num_cars,
                               num_clients=num_clients,
                               total_revenue=total_revenue)
    else:
        return 'You are not authorized to access this page.'



@app.route("/homeadmin")
def homeadmin():
    if 'email' in session:
        # Connect to the database
        conn = sqlite3.connect('loc.db')
        cursor = conn.cursor()

        # Fetch the last car added
        cursor.execute("SELECT * FROM voiture ORDER BY id_voiture DESC LIMIT 1")
        last_car_added = cursor.fetchone()

        # Fetch the last car reserved
        cursor.execute("SELECT voiture.*, reservation.id_client FROM voiture JOIN reservation ON voiture.id_voiture = reservation.id_voiture ORDER BY reservation.id_reservation DESC LIMIT 1")
        last_car_reserved = cursor.fetchone()

        # Fetch the last reservation
        cursor.execute("SELECT * FROM reservation ORDER BY id_reservation DESC LIMIT 1")
        last_reservation = cursor.fetchone()

        # Count the number of cars
        cursor.execute("SELECT COUNT(*) FROM voiture")
        num_cars = cursor.fetchone()[0]

        # Count the number of distinct managers
        cursor.execute("SELECT COUNT(*) FROM manager")
        num_managers = cursor.fetchone()[0]

        # Calculate the total revenue (sum of prices for accepted reservations)
        cursor.execute("SELECT SUM(voiture.prix) FROM reservation JOIN voiture ON reservation.id_voiture = voiture.id_voiture WHERE reservation.status = 'Accepted'")
        total_revenue = cursor.fetchone()[0] or 0

        # Close the database connection
        conn.close()

        # Render the home page with the fetched data
        return render_template("home-admin.html", 
                               last_car_added=last_car_added, 
                               last_car_reserved=last_car_reserved, 
                               last_reservation=last_reservation,
                               num_cars=num_cars,
                               num_managers=num_managers,
                               total_revenue=total_revenue)
    else:
        return 'You are not authorized to access this page.'


@app.route("/manager_dashboard")
def manager_dashboard():
    cars = manager.get_cars()
    if 'email' in session :
         return render_template(
        "add_car.html",
        cars=cars
    )
    else:
        return 'You are not authorized to access this page.'
   

@app.route("/manager_cars")
def manager_cars():
    cars = manager.get_cars()  # Assuming manager has a method to get the list of cars managed by the manager
    return render_template("manager_cars.html", cars=cars)


@app.route("/add_car", methods=["POST"])
def add_car():
    if request.method == "POST":
        # Get other car details from the form
        car_details = {
            "marque": request.form["marque"],
            "modele": request.form["modele"],
            "immatriculation": request.form["immatriculation"],
            "categorie": request.form["categorie"],
            "prix": request.form["prix"],
            "disponibilite": request.form["disponibilite"]
        }
        
        # Handle image upload
        if 'image_url' in request.files:
            image_file = request.files['image_url']
            # Save the image file to a folder
            image_filename = secure_filename(image_file.filename)  # Use secure_filename to sanitize the filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
            # Save the path to the image in the car_details dictionary
            car_details["image_url"] = image_path

        # Add the car to the database with other details
        manager.add_car(car_details)
        return redirect(url_for("manager_dashboard"))

@app.route("/modify_car/<int:car_id>", methods=["GET"])
def modify_car(car_id):
    # Fetch the car details from the database based on the car_id
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voiture WHERE id_voiture = ?", (car_id,))
    car = cursor.fetchone()
    conn.close()
    
    # Check if the car exists
    if car:
        # Construct a car object from the fetched data
        car_obj = Voiture(*car)
        # Render the template for modifying the car and pass the car object to it
        return render_template("modify_car.html", car=car_obj)
    else:
        return "Car not found", 404

@app.route("/modify_car/<int:car_id>", methods=["POST"])
def modify_car_post(car_id):
    if request.method == "POST":
        # Get car details from the form
        car_details = {
            "marque": request.form["marque"],
            "modele": request.form["modele"],
            "immatriculation": request.form["immatriculation"],
            "categorie": request.form["categorie"],
            "prix": request.form["prix"],
            "disponibilite": request.form["disponibilite"]
        }
        # Modify the car in the database
        manager.modify_car(car_id, car_details)
        return redirect(url_for("manager_cars"))


@app.route("/delete_car/<int:car_id>", methods=["POST"])
def delete_car(car_id):
    if request.method == "POST":
        # Delete the car from the database
        manager.delete_car(car_id)
        return redirect(url_for("manager_cars"))
    
manager = Manager(idManager="manager_id", nom="John", prenom="Doe", email="john@example.com", mot_de_passe="password")

def verify_manager_credentials(email, password):
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM manager WHERE email = ? AND mot_de_passe = ?", (email, password))
    manager = cursor.fetchone()
    conn.close()
    return manager

@app.route("/reservations")
def get_reservations():
    manager_instance = Manager(idManager="manager_id", nom="John", prenom="Doe", email="john@example.com", mot_de_passe="password")
    reservations = manager_instance.get_reservations()
    return render_template("reservations.html", reservations=reservations)


@app.route("/accept_reservation/<int:reservation_id>", methods=["POST"])
def accept_reservation(reservation_id):
    if request.method == "POST":
        # Call the accept_reservation method directly on the existing Manager instance
        manager.accept_reservation(reservation_id)
        return redirect(url_for("get_reservations"))

@app.route("/refuse_reservation/<int:reservation_id>", methods=["POST"])
def refuse_reservation(reservation_id):
    if request.method == "POST":
        # Get the car_id associated with the reservation
        manager.refuse_reservation(reservation_id)
        # Redirect to the page where reservations are listed
        return redirect(url_for("get_reservations"))



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        manager = verify_manager_credentials(email, password)
        if manager:
            session['email'] = email
            return redirect(url_for('home'))
        else:
            return "Invalid email or password"
    return render_template("login.html")

@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form['email']
        # Validate the email and authenticate the user
        # For simplicity, let's assume authentication is successful
        session['logged_in'] = True
        session['email'] = email
        return redirect('/reservation_status')
    return render_template('loginc.html')

@app.route('/reservation_status')
def reservation_status():
    if 'logged_in' in session:
        email = session['email']
        client_info = retrieve_client_info(email)
        if client_info:
            # Pass client information and reservations to the template
            return render_template('reservation_status.html', client=client_info)
        else:
            flash("Client information not found", "error")
            return redirect('/cus_login')
    else:
        return redirect('/cus_login')


def retrieve_client_info(email):
    conn = sqlite3.connect('loc.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client WHERE email=?", (email,))
    client_info = cursor.fetchone()
    if client_info:
        # Extract client information
        client_id, nom, prenom, _, telephone = client_info
        # Fetch reservations for the client
        cursor.execute("SELECT * FROM reservation inner join voiture on reservation.id_voiture = voiture.id_voiture WHERE reservation.id_client=?", (client_id,))
        reservations = cursor.fetchall()
        conn.close()
        return [
             client_id,
            nom,
             prenom,
            telephone,
             reservations
        ]
    else:
        conn.close()
        return None

@app.route("/cancel_reservation/<int:reservation_id>", methods=["POST"])
def cancel_reservation(reservation_id):
    if request.method == "POST":
        # Check if the user is logged in
        if 'logged_in' in session:
            # Retrieve the client's email from the session
            email = session['email']
            
            # Connect to the database
            conn = sqlite3.connect('loc.db')
            cursor = conn.cursor()
            
            # Retrieve the reservation and associated car_id from the database
            cursor.execute("SELECT * FROM reservation WHERE id_reservation=? AND id_client=(SELECT id_client FROM client WHERE email=?)", (reservation_id, email))
            reservation = cursor.fetchone()
            
            if reservation:
                car_id = reservation[1]  # Assuming car_id is in the second column of the reservation table
                
                # Update the reservation status to canceled
                cursor.execute("DELETE FROM reservation WHERE id_reservation=?", (reservation_id,))
                
                # Update the car's availability to 'available' in the car table
                cursor.execute("UPDATE voiture SET disponibilite='Disponible' WHERE id_voiture=?", (car_id,))
                
                # Commit changes and close connection
                conn.commit()
                conn.close()
                
                flash("Reservation canceled successfully", "success")
            else:
                flash("Reservation not found or you do not have permission to cancel it", "error")
            
            return redirect(url_for("reservation_status"))
        else:
            flash("Please log in to cancel reservations", "error")
            return redirect(url_for("customer_login"))

# Assuming you have an instance of the Client class named 'client'
client = Client(id_client=1, nom="John", prenom="Doe", email="john@example.com", telephone="123456789")

# Now call the get_reservations() method on the 'client' instance
reservations = client.get_reservations()



@app.route('/client_summary')
def client_summary():
    # Connect to the database
    conn = sqlite3.connect('loc.db')
    cursor = conn.cursor()

    # Fetch all clients from the 'client' table
    cursor.execute("SELECT * FROM client")
    clients = cursor.fetchall()

    # Initialize a list to store client summaries
    client_summaries = []

    # Iterate over each client
    for client in clients:
        client_id = client[0]
        nom = client[1]
        prenom = client[2]
        email = client[3]
        telephone = client[4]

        # Count the number of reservations for this client
        cursor.execute("SELECT COUNT(*) FROM reservation WHERE id_client=?", (client_id,))
        num_reservations = cursor.fetchone()[0]

        # Calculate the total amount spent by this client, excluding refused reservations
        cursor.execute("""
            SELECT SUM(voiture.prix) 
            FROM reservation 
            JOIN voiture ON reservation.id_voiture = voiture.id_voiture 
            WHERE reservation.id_client=? AND reservation.status != 'Refused'
        """, (client_id,))
        total_spent = cursor.fetchone()[0] or 0  # Handle None (no reservations)

        # Create a summary dictionary for this client
        summary = {
            'id': client_id,
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'telephone': telephone,
            'num_reservations': num_reservations,
            'total_spent': total_spent
        }

        # Append the summary to the list
        client_summaries.append(summary)

    # Close the database connection
    conn.close()

    # Pass the client summaries to the template
    return render_template('client_summary.html', client_summaries=client_summaries)

@app.route('/manager_profile', methods=['GET', 'POST'])
def manager_profile():
    if 'email' in session:
        email = session['email']

        # Connect to the database
        conn = sqlite3.connect('loc.db')
        cursor = conn.cursor()

        # Fetch manager's information based on email
        cursor.execute("SELECT * FROM manager WHERE email=?", (email,))
        manager_info = cursor.fetchone()

        conn.close()

        if not manager_info:
            return "Manager not found."

        if request.method == 'POST':
            # Extract updated information from the form
            nom = request.form['nom']
            prenom = request.form['prenom']
            email = request.form['email']
            mot_de_passe = request.form['mot_de_passe']  # For demonstration (should be securely handled)

            # Update manager's information in the database
            conn = sqlite3.connect('loc.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE manager SET nom=?, prenom=?, email=?, mot_de_passe=? WHERE email=?", (nom, prenom, email, mot_de_passe, email))
            conn.commit()
            conn.close()

            # Update session email if it has changed
            session['email'] = email

            return redirect('/manager_profile')

        # Render the manager profile template
        return render_template('manager_profile.html', manager_info=manager_info)

    else:
        return "You are not authorized to access this page."


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract client details from the form
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        telephone = request.form['telephone']

        # Insert the new client into the database
        conn = sqlite3.connect('loc.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO client (nom, prenom, email, telephone) VALUES (?, ?, ?, ?)", (nom, prenom, email, telephone))
        conn.commit()
        conn.close()

        # Redirect to a success page or another route
        return redirect('/signup_success')

    # Render the signup form template
    return render_template('resevation_form.html')

@app.route('/signup_success')
def signup_success():
    return render_template('signup_secces.html')




@app.route('/loginadmin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check admin credentials
        conn = sqlite3.connect('loc.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM administrateur WHERE email=? AND mot_de_passe=?", (email, password))
        admin = cursor.fetchone()
        conn.close()

        if admin:
            # Store admin email in session to track login state
            session['admin_email'] = email
            return redirect('/homeadmin')
        else:
            return "Invalid credentials. Please try again."

    # Render the login admin form
    return render_template('login_admin.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if is_admin_logged_in():
        # Fetch all managers
        conn = sqlite3.connect('loc.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM manager")
        managers = cursor.fetchall()
        conn.close()

        return render_template('admin_dashboard.html', managers=managers)
    else:
        return redirect('/loginadmin')
def is_admin_logged_in():
    return 'admin_email' in session
@app.route('/logout')
def logout():
    # Clear admin session data on logout
    session.pop('admin_email', None)
    return redirect('/loginadmin')


@app.route('/add_manager', methods=['GET', 'POST'])
def add_manager():
    if is_admin_logged_in():
        if request.method == 'POST':
            # Extract manager details from the form
            nom = request.form['nom']
            prenom = request.form['prenom']
            email = request.form['email']
            mot_de_passe = request.form['mot_de_passe']

            # Insert new manager into the database
            conn = sqlite3.connect('loc.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO manager (nom, prenom, email, mot_de_passe) VALUES (?, ?, ?, ?)",
                           (nom, prenom, email, mot_de_passe))
            conn.commit()
            conn.close()

            # Redirect to the admin dashboard after adding the manager
            return redirect('/admin_dashboard')
        
        # Render the add manager form
        return render_template('add_manager.html')
    else:
        return redirect('/loginadmin')

@app.route('/modify_manager/<int:manager_id>', methods=['GET', 'POST'])
def modify_manager(manager_id):
    if is_admin_logged_in():
        if request.method == 'POST':
            # Extract updated manager details from the form
            nom = request.form['nom']
            prenom = request.form['prenom']
            email = request.form['email']
            mot_de_passe = request.form['mot_de_passe']

            # Update the manager's information in the database
            conn = sqlite3.connect('loc.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE manager SET nom=?, prenom=?, email=?, mot_de_passe=? WHERE idManager=?",
                           (nom, prenom, email, mot_de_passe, manager_id))
            conn.commit()
            conn.close()

            # Redirect to the admin dashboard after modifying the manager
            return redirect('/admin_dashboard')

        # Fetch the manager's current information for pre-populating the form
        conn = sqlite3.connect('loc.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM manager WHERE idManager=?", (manager_id,))
        manager = cursor.fetchone()
        conn.close()

        if manager:
            return render_template('modify_manager.html', manager=manager)
        else:
            return "Manager not found."

    else:
        return redirect('/loginadmin')

@app.route('/delete_manager/<int:manager_id>')
def delete_manager(manager_id):
    if is_admin_logged_in():
        # Delete the manager from the database
        conn = sqlite3.connect('loc.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM manager WHERE idManager=?", (manager_id,))
        conn.commit()
        conn.close()

        # Redirect to the admin dashboard after deleting the manager
        return redirect('/admin_dashboard')

    else:
        return redirect('/loginadmin')
 
    
if __name__ == "__main__":
 app.run(debug=True)
