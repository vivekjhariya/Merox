from fastapi import FastAPI
import redis
import psycopg2
import pymongo
from cassandra.cluster import Cluster
from kafka import KafkaProducer
import json
import os
import time

app = FastAPI()

# Redis
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=6379, decode_responses=True)

# PostgreSQL
pg_conn = psycopg2.connect(
    dbname="medicine_db", user="user", password="password", host=os.getenv('POSTGRES_HOST', 'postgres')
)

# MongoDB
mongo_client = pymongo.MongoClient(f"mongodb://{os.getenv('MONGODB_HOST', 'mongodb')}:27017/")
mongo_db = mongo_client["medicine_db"]

# Cassandra with retry
cassandra_cluster = Cluster([os.getenv('CASSANDRA_HOST', 'cassandra')], port=9042)
max_retries = 10
for i in range(max_retries):
    try:
        cassandra_session = cassandra_cluster.connect()
        print("Connected to Cassandra successfully")
        break
    except Exception as e:
        print(f"Failed to connect to Cassandra: {e}. Retrying ({i+1}/{max_retries})...")
        time.sleep(5)
else:
    raise Exception("Could not connect to Cassandra after multiple attempts")

# Kafka
producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA_BROKER', 'kafka:9092'), value_serializer=lambda v: json.dumps(v).encode('utf-8'))

@app.get("/cart/{user_id}")
def get_cart(user_id: str):
    cart = redis_client.get(f"user:{user_id}:cart")
    return json.loads(cart) if cart else {"items": []}

@app.post("/cart/{user_id}")
def add_to_cart(user_id: str, item: dict):
    cart = redis_client.get(f"user:{user_id}:cart")
    cart_data = json.loads(cart) if cart else {"items": []}
    cart_data["items"].append(item)
    redis_client.setex(f"user:{user_id}:cart", 86400, json.dumps(cart_data))
    producer.send('orders', {"user_id": user_id, "item": item})
    return {"message": "Item added"}
