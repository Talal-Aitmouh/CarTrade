import sqlite3 as sql
import sqlite3
import os

class Manager:
    def __init__(self, idManager, nom, prenom, email, mot_de_passe):
        self.idManager = idManager
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.mot_de_passe = mot_de_passe


    def save_image(self, image):
        # Get the filename
        filename = image.filename
        # Create a path to the uploads folder
        uploads_dir = os.path.join(self.app.root_path, 'static', 'photo')
        # Save the image to the uploads folder
        image.save(os.path.join(uploads_dir, filename))
        # Return the path to the saved image
        return os.path.join('static', 'photo', filename)
    def connect_to_database(self):
        return sql.connect("loc.db")
    
    def get_cars(self):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM voiture")
        cars_data = cursor.fetchall()
        conn.close()

        # Convert fetched data to list of dictionaries
        cars = []
        for car in cars_data:
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
            cars.append(car_dict)
        return cars

    def add_car(self, car_details):
        conn = self.connect_to_database()
        cursor = conn.cursor()
        cursor.execute(
    "INSERT INTO voiture (marque, modele, immatriculation, categorie, prix, disponibilite, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
    (
        car_details["marque"],
        car_details["modele"],
        car_details["immatriculation"],
        car_details["categorie"],
        car_details["prix"],
        car_details["disponibilite"],
        car_details["image_url"]
    ),
)

        conn.commit()
        conn.close()

    def modify_car(self, car_id, car_details):
        conn = self.connect_to_database()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE voiture SET marque=?, modele=?, immatriculation=?, categorie=?, prix=?, disponibilite=? WHERE id_voiture=?",
            (
                car_details["marque"],
                car_details["modele"],
                car_details["immatriculation"],
                car_details["categorie"],
                car_details["prix"],
                car_details["disponibilite"],
                car_id,
            ),
        )
        conn.commit()
        conn.close()

    def delete_car(self, car_id):
        conn = self.connect_to_database()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM voiture WHERE id_voiture=?", (car_id,))
        conn.commit()
        conn.close()

    def get_reservations(self):
      conn = sqlite3.connect("loc.db")
      cursor = conn.cursor()

# Select required columns from 'reservation' and join with 'voiture' and 'client' tables
      cursor.execute("""
           SELECT reservation.id_reservation, reservation.id_client, reservation.id_voiture, reservation.status, reservation.id_manager,
           voiture.marque, voiture.modele, voiture.immatriculation, voiture.categorie, voiture.prix, voiture.disponibilite, voiture.image_url,
           client.nom, client.prenom
           FROM reservation
           INNER JOIN voiture ON reservation.id_voiture = voiture.id_voiture
           INNER JOIN client ON reservation.id_client = client.id_client
           """)
      reservations_data = cursor.fetchall()
      conn.close()

      reservations = []
      for row in reservations_data:
        reservation = {
        "id_reservation": row[0],
        "id_client": row[1],
        "id_voiture": row[2],
        "status": row[3],
        "id_manager": row[4],
        "marque": row[5],
        "modele": row[6],
        "immatriculation": row[7],
        "categorie": row[8],
        "prix": row[9],
        "disponibilite": row[10],
        "image_url": row[11],
        "client_nom": row[12],
        "client_prenom": row[13]
        }
        reservations.append(reservation)

      return reservations


    def accept_reservation(self, id_reservation):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()

    # Update reservation status to 'Accepted'
        cursor.execute(
            "UPDATE reservation SET status='Accepted' WHERE id_reservation=?", (id_reservation,)
        )

    # Fetch the id_voiture associated with this reservation
       
        conn.commit()
        conn.close()
    def refuse_reservation(self, reservation_id):
        conn = sqlite3.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id_voiture FROM reservation WHERE id_reservation = ?", (reservation_id,))
        car_id = cursor.fetchone()[0]
        
        # Update the car's availability to 'disponible' in the database
        cursor.execute("UPDATE voiture SET disponibilite = ? WHERE id_voiture = ?", ('Disponible', car_id))
        
        # Update the reservation status to 'Refused' in the database
        cursor.execute("UPDATE reservation SET status = ? WHERE id_reservation = ?", ('Refused', reservation_id))
        
        conn.commit()
        conn.close()

        # Redirect to the page where reservations are listed


