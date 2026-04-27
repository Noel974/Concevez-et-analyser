from db.mongo_connection import get_dataframe
import polars as pl

df = get_dataframe()

# Nettoyage des colonnes
df = df.with_columns([
    pl.col("availability_365")
        .cast(pl.Int64, strict=False)
        .fill_null(0),

    pl.col("neighbourhood_cleansed")
        .cast(pl.Utf8, strict=False)
        .fill_null("Inconnu")
])

# Calcul du taux de réservation annuel
df = df.with_columns(
    ((365 - pl.col("availability_365")) / 365)
        .alias("reservation_rate")
)

# Taux moyen par quartier
result = df.group_by("neighbourhood_cleansed").agg(
    pl.col("reservation_rate").mean().alias("avg_reservation_rate")
).sort("avg_reservation_rate", descending=True)

print("Top 10 des quartiers avec le plus fort taux de réservation :")
print(result.head(10))
