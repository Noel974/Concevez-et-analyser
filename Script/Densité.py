from db.mongo_connection import get_dataframe
import polars as pl

df = get_dataframe()

# Nettoyage de la colonne neighbourhood
df = df.with_columns(
    pl.col("neighbourhood_cleansed")
        .cast(pl.Utf8, strict=False)
        .fill_null("Inconnu")
)

# Densité de logements par quartier
result = df.group_by("neighbourhood_cleansed").agg(
    pl.count().alias("nb_logements")
).sort("nb_logements", descending=True)

print("Densité de logements par quartier de Paris :")
print(result)
