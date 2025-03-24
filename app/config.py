from dotenv import load_dotenv
import os

# Always load .env from the root of the project
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY not found in .env file!")

# print("GOOGLE_API_KEY loaded: Loaded")
