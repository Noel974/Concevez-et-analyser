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

if not all([MONGO_USER, MONGO_PASSWORD, MONGO_DB_NAME, MONGO_COLLECTION]):
    raise ValueError("❌ Vérifie tes variables d'environnement (.env)")

# ==============================
#  Construction de l'URI sécurisée
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
#  Récupération des quartiers uniquement
# ==============================
data = list(collection.find(
    {},
    {
        "neighbourhood_cleansed": 1,
        "_id": 0
    }
))

# ==============================
#  Conversion en DataFrame Polars
# ==============================
df = pl.DataFrame(data)

# ==============================
# Nettoyage : suppression des valeurs nulles
# ==============================
df = df.drop_nulls("neighbourhood_cleansed")

# ==============================
#  Comptage du nombre de logements par quartier
# ==============================
result = (
    df.group_by("neighbourhood_cleansed")
      .agg(pl.count().alias("nombre_logements"))
      .sort("nombre_logements", descending=True)
)

# ==============================
#  Affichage
# ==============================
print("📊 Densité de logements par quartier :")
print(result)