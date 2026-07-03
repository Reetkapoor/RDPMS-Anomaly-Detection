import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
import joblib

DATABASE_URL = "postgresql://postgres:reet@localhost:5432/rdpms"

engine = create_engine(DATABASE_URL)

df = pd.read_sql(
    """
    SELECT voltage,current,temperature,humidity
    FROM sensor_readings
    """,
    engine
)

model = IsolationForest(
    contamination=0.05,
    random_state=42
)

model.fit(df)

joblib.dump(model, "ml/anomaly/isolation_forest.pkl")

print("Model trained successfully!")