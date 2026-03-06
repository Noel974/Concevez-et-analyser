import pandas as pd
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from urllib.parse import quote_plus

print(os.getcwd())

# ==============================
# Chargement des variables d'environnement
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
# Construction de l'URI sécurisée
# ==============================
user = quote_plus(MONGO_USER)
password = quote_plus(MONGO_PASSWORD)

MONGO_URI = f"mongodb://{user}:{password}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"

# ==============================
# Chemin du CSV
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "data", "listings_Lyon.csv")

# ==============================
# Connexion MongoDB
# ==============================
try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION]

    print("Connexion réussie ✅")

    # ==============================
    # 1. Mise à jour des documents PARIS
    # ==============================
    update_result = collection.update_many(
        {"city": {"$exists": False}},
        {"$set": {"city": "Paris"}}
    )

    if update_result.modified_count > 0:
        print(f"✔️ {update_result.modified_count} documents Paris mis à jour avec city='Paris'")
    else:
        print("ℹ️ Aucun document Paris à mettre à jour (peut-être déjà fait)")

    # ==============================
    # 2. Import des données de Lyon
    # ==============================
    df_lyon = pd.read_csv(csv_path)
    df_lyon["city"] = "Lyon"

    documents_lyon = df_lyon.to_dict(orient="records")
    result = collection.insert_many(documents_lyon)

    print(f"✔️ {len(result.inserted_ids)} documents Lyon insérés avec succès.")

except Exception as e:
    print("❌ Erreur :", e)

finally:
    client.close()
