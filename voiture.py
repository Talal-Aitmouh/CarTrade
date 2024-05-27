class Voiture:
    def __init__(
        self,
        id_voiture,
        marque,
        modele,
        immatriculation,
        categorie,
        prix,
        disponibilite=True,
        image_url=None,
    ):
        self.id = id_voiture
        self.marque = marque
        self.modele = modele
        self.immatriculation = immatriculation
        self.categorie = categorie
        self.prix = prix
        self.disponibilite = disponibilite
        self.image_url = image_url

    def get_details(self):
        return f"Marque: {self.marque}, Modèle: {self.modele}, Immatriculation: {self.immatriculation}, Catégorie: {self.categorie}, Prix: {self.prix}, Disponible: {self.disponible}, Image URL: {self.image_url}"

    def reserve(self):
        if self.disponible:
            self.disponible = False
            return "Reservation successful."
        else:
            return "Car is not available for reservation."
    
    def cancel_reservation(self):
        if not self.disponible:
            self.disponible = True
            return "Reservation canceled."
        else:
            return "No reservation to cancel."


