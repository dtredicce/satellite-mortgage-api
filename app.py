from flask import Flask, request, jsonify
from satellite_processor import analyze_satellite_image
from banco_nacion_scraper import simulate_banco_nacion  # ✅ correct import

app = Flask(__name__)

@app.route('/')
def home():
    return "API activa para simulaciones y análisis satelital."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    image_url = data.get("image_url")
    result = analyze_satellite_image(image_url)
    return jsonify(result)

@app.route('/simulate-mortgage', methods=['POST'])  # ✅ this is your endpoint/route
def simulate_mortgage():
    data = request.get_json()
    banco = data.get("banco")

    if banco == "nacion":
        result = simulate_banco_nacion(data)
        return jsonify(result)
    else:
        return jsonify({"error": "Banco no soportado"}), 400

if __name__ == '__main__':
    app.run()
