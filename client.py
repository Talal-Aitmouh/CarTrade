import sqlite3 as sql
from voiture import Voiture
import sqlite3

class Client:
    def __init__(self, id_client, nom, prenom, email, telephone):
        self.id_client = id_client
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.telephone = telephone
        self.reservations = []
    def getClients(self):
        return {
            "id Client" : self.id_client,
            "nom" : self.nom,
            "prenom" : self.prenom,
            "email": self.email,
            "tel": self.telephone
        }
    def get_reservations(self):
        def get_reservations(self):
         conn = sqlite3.connect("loc.db")
         cursor = conn.cursor()
         cursor.execute("""
            SELECT reservation.id_reservation, reservation.id_client, reservation.id_voiture, reservation.status, 
                   reservation.id_manager, voiture.marque, voiture.modele, voiture.immatriculation, voiture.categorie, 
                   voiture.prix, voiture.disponibilite, voiture.image_url, client.nom, client.prenom
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



    def reserver_voiture(self, voiture_id):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT disponibilite FROM voiture WHERE id_voiture=?", (voiture_id,)
        )
        disponibilite = cursor.fetchone()
        if disponibilite and disponibilite[0] == "Disponible":
            cursor.execute(
                "UPDATE voiture SET disponibilite='Non disponible' WHERE id_voiture=?",
                (voiture_id,),
            )
            cursor.execute(
                "INSERT INTO reservations (client_id, voiture_id) VALUES (?, ?)",
                (self.id, voiture_id),
            )
            conn.commit()
            print("La voiture a été réservée avec succès.")
        else:
            print("La voiture est déjà réservée ou n'est pas disponible.")
        conn.close()

    def annuler_reservation(self, reservation_id):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM reservations WHERE id_reservation=? AND client_id=?",
            (reservation_id, self.id),
        )
        reservation = cursor.fetchone()
        if reservation:
            cursor.execute(
                "UPDATE voiture SET disponibilite='Disponible' WHERE id_voiture=?",
                (reservation[2],),
            )
            cursor.execute(
                "DELETE FROM reservations WHERE id_reservation=?", (reservation_id,)
            )
            conn.commit()
            print("La réservation de la voiture a été annulée.")
        else:
            print("Aucune réservation trouvée pour ce client avec l'identifiant donné.")
        conn.close()
