import sqlite3 as sql
from manager import Manager


class Administrator:
    def __init__(self, idAdministrateur, nom, prenom, email, mot_de_passe):
        self.idAdministrateur = idAdministrateur
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.mot_de_passe = mot_de_passe

    def get_managers(self):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM manager")
        managers = cursor.fetchall()
        conn.close()

        # Create a list of dictionaries containing manager information
        manager_list = []
        for manager in managers:
            manager_dict = {
                "id": manager[0],
                "nom": manager[1],
                "prenom": manager[2],
                "email": manager[3],
                "mot_de_passe": manager[4]
            }
            manager_list.append(manager_dict)

        return manager_list


    def add_manager(self, manager_details):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO manager (nom, prenom, email, mot_de_passe) VALUES (?, ?, ?, ?)",
            (
                manager_details["nom"],
                manager_details["prenom"],
                manager_details["email"],
                manager_details["mot_de_passe"],
            ),
        )
        conn.commit()
        conn.close()

    def modify_manager(self, manager_id, manager_details):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE manager SET nom=?, prenom=?, email=?, mot_de_passe=? WHERE id=?",
            (   manager_id,
                manager_details["nom"],
                manager_details["prenom"],
                manager_details["email"],
                manager_details["mot_de_passe"],
                
            ),
        )
        conn.commit()
        conn.close()

    def delete_manager(self, manager_id):
        conn = sql.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM manager WHERE id=?", (manager_id,))
        conn.commit()
        conn.close()
