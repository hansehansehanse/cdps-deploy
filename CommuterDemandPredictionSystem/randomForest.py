
import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from .models import HistoricalDataset  # adjust as necessary

def train_random_forest_model():
    queryset = HistoricalDataset.objects.all()                                              #i think i also need to add temporal dataset
    data = pd.DataFrame(list(queryset.values()))

    # Feature engineering
    data['hour'] = data['time'].apply(lambda x: x.hour)
    data['day_of_week'] = data['date'].apply(lambda x: x.weekday())

    # Ensure 'num_commuters' exists
    if 'num_commuters' not in data.columns:
        print("❌ 'num_commuters' column is missing")
        return None

    # Check for missing values
    if data.isnull().any().any():
        print("❌ Data contains missing values:")
        print(data.isnull().sum())
        return None

    # Encode route using LabelEncoder
    if 'route' not in data.columns:
        print("❌ 'route' column is missing")
        return None
    
    route_encoder = LabelEncoder()
    data['route'] = route_encoder.fit_transform(data['route'])

    features_to_use = [
        'hour', 'route', 'day_of_week', 'is_holiday', 'is_friday', 'is_saturday', 'is_local_event',
        'is_others', 'is_flagged', 'is_day_before_holiday', 'is_long_weekend', 
        'is_day_before_long_weekend', 'is_end_of_sem', 'is_day_before_end_of_sem', 
        'is_day_after_end_of_sem', 'is_2days_after_end_of_sem', 'is_local_holiday', 
        'is_start_of_sem', 'is_week_after_end_of_sem', 'is_week_before_end_of_sem', 
        'is_within_ay'
    ]

    missing_features = [f for f in features_to_use if f not in data.columns]
    if missing_features:
        print(f"❌ Missing features in data: {missing_features}")
        return None

    X = data[features_to_use]
    y = data['num_commuters']

    # Split and train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # Evaluation
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)

    # Save everything
    save_model_and_results(model, rmse, mae, features_to_use, route_encoder)

    # return model
    return model, f"RMSE: {rmse:.2f}, MAE: {mae:.2f}"


import os
import joblib
from datetime import datetime
from .models import ModelTrainingHistory
from CommuterDemandPredictionSystem.models import HistoricalDataset
from .supabase_utils import upload_file

def save_model_and_results(model, rmse, mae, features_to_use, route_encoder, trained_by=None):


    print(f"[{datetime.now()}] 🚀 Starting model saving process...")

    model_dir = os.path.join(os.path.dirname(__file__), 'model')
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, 'random_forest_model.pkl')
    features_path = os.path.join(model_dir, 'features_used.pkl')
    encoder_path = os.path.join(model_dir, 'route_encoder.pkl')
    metrics_path = os.path.join(model_dir, 'model_results.txt')

    print(f"[{datetime.now()}] 💾 Saving model to {model_path}")
    joblib.dump(model, model_path)

    print(f"[{datetime.now()}] 💾 Saving features to {features_path}")
    joblib.dump(features_to_use, features_path)

    print(f"[{datetime.now()}] 💾 Saving route encoder to {encoder_path}")
    joblib.dump(route_encoder, encoder_path)

    print(f"[{datetime.now()}] 📄 Writing metrics to {metrics_path}")
    with open(metrics_path, 'w') as f:
        f.write("Random Forest Model Evaluation Results\n")
        f.write(f"RMSE: {rmse:.2f}\n")
        f.write(f"MAE: {mae:.2f}\n")
        f.write(f"Date of Training: {datetime.now()}\n")

    print(f"[{datetime.now()}] 📅 Fetching date range from HistoricalDataset")
    oldest_date = HistoricalDataset.objects.order_by('date').first().date
    latest_date = HistoricalDataset.objects.order_by('-date').first().date

    model_type = 'Random Forest'
    model_name = f"{model_type} ({oldest_date.strftime('%Y-%m-%d')} to {latest_date.strftime('%Y-%m-%d')})"

    print(f"[{datetime.now()}] 🧹 Clearing old training history")
    ModelTrainingHistory.objects.all().delete()

    print(f"[{datetime.now()}] 🧾 Saving training metadata to DB")
    ModelTrainingHistory.objects.create(
        model_type=model_type,
        model_name=model_name,
        rmse=rmse,
        mae=mae,
        oldest_date=oldest_date,
        latest_date=latest_date,
    )
    
    print(f"[{datetime.now()}] ☁️ Uploading files to Supabase")
    upload_file(model_path, 'models/random_forest_model.pkl')
    upload_file(features_path, 'models/features_used.pkl')
    upload_file(encoder_path, 'models/route_encoder.pkl')
    upload_file(metrics_path, 'models/model_results.txt')

