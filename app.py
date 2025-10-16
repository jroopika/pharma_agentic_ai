# empty
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from agents.master_agent import MasterAgent
from pathlib import Path


app = Flask(__name__)
CORS(app)  # Enable CORS for React development
master = MasterAgent()


@app.route("/", methods=["GET"])
def index():
	return jsonify({"service": "pharma_agentic_ai", "status": "ready"})


@app.route("/analyze", methods=["POST"])
def analyze():
	payload = request.get_json(force=True)
	drug = payload.get("drug") if payload else None
	if not drug:
		return jsonify({"error": "Please provide 'drug' in JSON body"}), 400
	result = master.analyze(drug)
	return jsonify(result)


@app.route("/reports/<path:filename>", methods=["GET"])
def get_report(filename):
	reports_dir = Path(__file__).parent / "outputs" / "reports"
	if not (reports_dir / filename).exists():
		return jsonify({"error": "File not found"}), 404
	return send_from_directory(directory=str(reports_dir), path=filename, as_attachment=True)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)

