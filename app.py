from flask import Flask, request, jsonify
from satellite_processor import analyze_satellite_image
from banco_nacion_scraper import simulate_banco_nacion  # ✅ import correcto

app = Flask(__name__)

@app.route('/')
def home():
    return "API activa para simulaciones y análisis satelital."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    image_url = data.get("image_url")
    print(">>> Análisis satelital recibido:", image_url)

    try:
        result = analyze_satellite_image(image_url)
        print(">>> Resultado del análisis:", result)
        return jsonify(result)
    except Exception as e:
        print(">>> ERROR en análisis satelital:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/simulate-mortgage', methods=['POST'])  # ✅ endpoint de simulación
def simulate_mortgage():
    data = request.get_json()
    banco = data.get("banco")
    print(">>> Data recibida en /simulate-mortgage:", data)

    if banco == "nacion":
        try:
            result = simulate_banco_nacion(data)
            print(">>> Resultado de simulación Banco Nación:", result)
            return jsonify(result)
        except Exception as e:
            print(">>> ERROR en simulación Banco Nación:", e)
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Banco no soportado"}), 400

if __name__ == '__main__':
    app.run()
