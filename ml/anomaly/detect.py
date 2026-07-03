import pandas as pd
import joblib
import time

from sqlalchemy import create_engine,text

DATABASE_URL = "postgresql://postgres:reet@localhost:5432/rdpms"

engine = create_engine(DATABASE_URL)

model = joblib.load("ml/anomaly/models/isolation_forest.pkl")

query = """
SELECT *
FROM sensor_readings
ORDER BY reading_id DESC
LIMIT 1
"""
while True:
    df = pd.read_sql(query, engine)

    features = df[
        ["voltage","current","temperature","humidity"]
    ]

    prediction = model.predict(features)

    if prediction[0] == -1:

        asset_id = int(df["asset_id"].iloc[0])

        with engine.begin() as conn:

            conn.execute(
                text("""
                    INSERT INTO alerts
                    (asset_id, alert_type, severity, message)

                    VALUES
                    (:asset_id,:alert_type,:severity,:message)
                """),
                {
                    "asset_id": asset_id,
                    "alert_type": "Anomaly",
                    "severity": "High",
                    "message": "Abnormal sensor behaviour detected"
                }
            )

        print("ANOMALY DETECTED")

    else:

        print("Normal")

    time.sleep(2)