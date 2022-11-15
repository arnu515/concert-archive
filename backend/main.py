from dotenv import load_dotenv
from src import app
import os

load_dotenv()

if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 5000)), debug=True, auto_reload=True)
