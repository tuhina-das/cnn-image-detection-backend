# run.py
from flask import Flask
from comparison import comparison_bp
from scrape import scrape_bp

app = Flask(__name__)

# Register your routes
app.register_blueprint(comparison_bp)
app.register_blueprint(scrape_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render requires a port binding
