from app import create_app
import certifi
import os

# Ensure SSL certificates are loaded
os.environ['SSL_CERT_FILE'] = certifi.where()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
