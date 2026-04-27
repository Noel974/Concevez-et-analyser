from db.mongo_connection import get_dataframe
import polars as pl

df = get_dataframe()

# Convertir number_of_reviews en entier
df = df.with_columns(
    pl.col("number_of_reviews")
        .cast(pl.Int64, strict=False)
        .fill_null(0)
)

# Calcul de la médiane par catégorie d'hôte
result = df.group_by("host_is_superhost").agg(
    pl.col("number_of_reviews").median().alias("median_reviews")
)

print("Médiane du nombre d'avis par catégorie d'hôte :")
print(result)
