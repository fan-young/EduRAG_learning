import os
import redis

client = redis.Redis(
    host="localhost",
    port=6379,
    password=os.environ["REDIS_PASSWORD"],
    decode_responses=True,
)

client.set("test_key", "Hello, Redis!")
print(f"Redis value: {client.get('test_key')}")