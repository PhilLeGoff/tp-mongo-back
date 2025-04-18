from app import create_app
import certifi
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure SSL certificates are loaded
os.environ['SSL_CERT_FILE'] = certifi.where()

app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_RUN_PORT", 5000)),
        debug=True
    )