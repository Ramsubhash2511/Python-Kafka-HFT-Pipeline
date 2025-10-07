import pandas as pd
from kafka import KafkaProducer
import json
import time

# --- Configuration ---
KAFKA_TOPIC = 'crypto-market-data'
KAFKA_SERVER = 'localhost:9092'
CSV_FILE_PATH = 'processed_trading_data2.csv'
SIMULATION_SPEED = 0.1 # seconds per message

# --- Kafka Producer Setup ---
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("Successfully connected to Kafka.")
except Exception as e:
    print(f"Error connecting to Kafka: {e}")
    exit()

print("Reading CSV and preparing to stream data...")
# Read a sample of the data to keep the stream manageable
df = pd.read_csv(CSV_FILE_PATH, nrows=5000)

# Use the correct column names from your data
print(f"Streaming {len(df)} rows to Kafka topic '{KAFKA_TOPIC}'...")

# --- Data Streaming Loop ---
for index, row in df.iterrows():
    # Create a dictionary from the row data using your column names
    message = {
        'timestamp': row['datetime'],
        'open': row['open'],
        'high': row['high'],
        'low': row['low'],
        'close': row['close'],
        'volume': row['volume']
    }
    
    # Send the message to the Kafka topic
    producer.send(KAFKA_TOPIC, value=message)
    
    print(f"Sent: {message['timestamp']} | Close: {message['close']}")
    
    time.sleep(SIMULATION_SPEED)

producer.flush()
print("Finished streaming data.")