from db.mongo_connection import get_dataframe
import polars as pl

df = get_dataframe()

# Convertir availability_30 en entier
df = df.with_columns(
    pl.col("availability_30")
        .cast(pl.Int64, strict=False)
        .fill_null(0)
)

# Calcul du taux de réservation
df = df.with_columns(
    ((pl.col("availability_30") / 30) * 100)
    .alias("reservation_rate_30")
)

# Agrégation par type de logement
taux_moyen_par_type = df.group_by("room_type").agg(
    pl.col("reservation_rate_30").mean().alias("taux_moyen_reservation")
)

print("Taux moyen de réservation par type de logement :")
print(taux_moyen_par_type)
