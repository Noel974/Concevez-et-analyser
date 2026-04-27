import os
import json
import urllib.parse
from datetime import datetime, date

from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
import polars as pl

# Chargement des variables d'environnement
load_dotenv()


# ---------------------------------------------------------
# Normalisation des valeurs MongoDB → valeurs compatibles Polars / Pandas
# ---------------------------------------------------------
def normalize_value(value):
    """Normalise une valeur MongoDB pour la rendre compatible avec Polars/Pandas."""

    if isinstance(value, ObjectId):
        return str(value)

    if isinstance(value, (list, dict)):
        return json.dumps(value) if value else None

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if value is None:
        return None

    if isinstance(value, (int, float, str, bool)):
        return value

    return str(value)


def normalize_document(doc):
    """Normalise un document MongoDB entier."""
    return {key: normalize_value(value) for key, value in doc.items()}


# ---------------------------------------------------------
# Chargement de la collection MongoDB → DataFrame Polars ou Pandas
# ---------------------------------------------------------
def get_dataframe(as_pandas=False):
    """
    Charge une collection MongoDB et renvoie :
    - un DataFrame Polars (par défaut)
    - un DataFrame Pandas (si as_pandas=True, utile pour Power BI)
    """

    # Lecture des variables d'environnement
    user = urllib.parse.quote_plus(os.getenv("MONGO_USER"))
    password = urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD"))
    host = os.getenv("MONGO_HOST")
    port = os.getenv("MONGO_PORT", "27017")
    db_name = os.getenv("MONGO_DB_NAME")
    collection_name = os.getenv("MONGO_COLLECTION")

    # Construction de l'URI MongoDB
    mongo_uri = (
        f"mongodb://{user}:{password}@{host}:{port}/"
        "?authMechanism=DEFAULT&authSource=admin"
    )

    # Connexion MongoDB
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Extraction des documents
    data = list(collection.find())

    # Normalisation
    normalized_data = [normalize_document(doc) for doc in data]

    # Conversion en DataFrame Polars
    df_polars = pl.DataFrame(normalized_data, infer_schema_length=None)

    # Conversion pour Power BI (Pandas)
    if as_pandas:
        return df_polars.to_pandas()

    return df_polars
