from db.mongo_connection import get_dataframe
import polars as pl

df = get_dataframe()

# Convertir number_of_reviews en entier
df = df.with_columns(
    pl.col("number_of_reviews")
        .cast(pl.Int64, strict=False)
        .fill_null(0)
)

# Calcul de la médiane
result = df.select(
    pl.col("number_of_reviews").median().alias("median_number_of_reviews")
)

print("La médiane du nombre d’avis pour tous les logements :")
print(result)
