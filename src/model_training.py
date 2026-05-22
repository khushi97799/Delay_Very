import pandas as pd

from sklearn.model_selection import (
    train_test_split
)

from sklearn.metrics import (
    mean_absolute_error
)

from xgboost import XGBRegressor
df = pd.read_csv(
    "data/processed/final_data.csv"
)

features = [

    'osrm_distance',

    'hour',

    'peak_hour',

    'source_degree',

    'source_betweenness',

    'source_pagerank',

    'source_clustering'
]

target = 'delay'

X = df[features]

y = df[target]

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )
)

model = XGBRegressor(

    n_estimators=300,

    learning_rate=0.05,

    max_depth=8,

    subsample=0.8,

    colsample_bytree=0.8
)

model.fit(X_train, y_train)

preds = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    preds
)

print("MAE:", mae)
import joblib
import os

os.makedirs("models", exist_ok=True)

joblib.dump(
    model,
    "models/xgb_model.pkl"
)