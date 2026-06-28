import os
import requests
import pandas as pd
from datetime import datetime, timezone
from google.cloud import storage

CITIES = [
    {"name": "São Paulo", "lat": -23.5500, "lon": -46.6330},
    {"name": "Manaus", "lat": -3.10719, "lon": -60.0261},
    {"name": "Rio de Janeiro", "lat": -22.908333, "lon": -43.196388},
    {"name": "Porto Alegre", "lat": -30.033, "lon": -51.230},
    {"name": "Fortaleza", "lat": -3.71839, "lon": -38.5434},
]

HOURLY_PARAMS = [
    "temperature_2m",
    "apparent_temperature",
    "precipitation_probability",
    "precipitation",
    "relative_humidity_2m",
    "uv_index",
    "wind_speed_10m",
    "wind_gusts_10m",
    "cloud_cover",
    "weather_code",
]

def fetch_weather(city):
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "hourly": HOURLY_PARAMS, 
        "timezone": "UTC",
        "forecast_days": 1
    }

    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
        
        response.raise_for_status()
        
        data = response.json()
        
        return data
    
    except requests.exceptions.HTTPError as erro_http:
        
        print(f"Erro na busca dos dados de {city['name']}: {erro_http}")
        
        return None

def parse_weather(data, city):
    
    hourly = data["hourly"]

    df = pd.DataFrame(hourly)

    df["city"] = city["name"]
    df["extracted_at"] = datetime.now(timezone.utc).isoformat()
    
    return df

def save_to_gcs(df, city):
    bucket_name = os.getenv("GCP_BUCKET_RAW")
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H")
    filename = f"weather/{city['name']}/{timestamp}.parquet"

    blob = bucket.blob(filename)
    blob.upload_from_string(
        df.to_parquet(index=False),
        content_type="application/octet-stream"
    )
    print(f"Salvo: {filename}")

def run():
    
    for capital in CITIES: 
        print(f"Extraindo dados de {capital ['name']}")

        data = fetch_weather(capital)

        if data is None:
            continue

        df = parse_weather(data, capital)

        save_to_gcs(df, capital)

if __name__ == "__main__":
    run()
