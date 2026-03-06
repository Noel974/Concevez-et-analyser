# ==============================
#  Import des librairies
# ==============================
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from urllib.parse import quote_plus
import polars as pl

# ==============================
#  Chargement des variables d'environnement
# ==============================
load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")        
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# ==============================
# 3️⃣ Construction de l'URI sécurisée
# ==============================
user = quote_plus(MONGO_USER)
password = quote_plus(MONGO_PASSWORD)

MONGO_URI = f"mongodb://{user}:{password}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"

# ==============================
# Connexion à MongoDB
# ==============================
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION]

print("Connexion réussie ✅")

# ==============================
#  Récupération et nettoyage des données
# ==============================
data = list(collection.find({}))
cleaned_data = []

for doc in data:
    # Supprimer l'ID MongoDB
    doc.pop("_id", None)
    # Remplacer les listes vides par None
    for key, value in doc.items():
        if value == []:
            doc[key] = None
    cleaned_data.append(doc)

# ==============================
#  Conversion en DataFrame Polars
# ==============================
df = pl.DataFrame(cleaned_data, infer_schema_length=10000)

# ==============================
# Calcul du taux de réservation sur 30 jours
# ==============================
# On suppose que availability_30 contient le nombre de jours réservés
df = df.with_columns(
    ((pl.col("availability_30").cast(pl.Float64) / 30) * 100)
    .alias("reservation_rate_30")
)

# ==============================
#  Calcul du taux moyen par type de logement
# ==============================
taux_moyen_par_type = df.group_by("room_type").agg(
    pl.col("reservation_rate_30").mean().alias("taux_moyen_reservation")
)

# ==============================
#  Affichage du résultat
# ==============================
print("Taux moyen de réservation par type de logement :")
print(taux_moyen_par_type)