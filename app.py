import os
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- Initialize Firebase Admin using service account JSON path in env var ---
if "FIREBASE_KEY" in os.environ:
    with open("firebase-key.json", "w") as f:
        f.write(os.environ["FIREBASE_KEY"])
    cred_path = "firebase-key.json"
else:
    # Local fallback (you can still use your local JSON in VS Code)
    cred_path = "C:\Users\charu\Downloads\basic1-3f3e3-firebase-adminsdk-fbsvc-063b0ac330.json"
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()
cities = db.collection("cities")

@app.route("/")
def home():
    return "Simple Cities API — endpoints: GET /city/<name>, POST /city, PUT /city/<name>, DELETE /city/<name>"

# READ
@app.route("/city/<city_name>", methods=["GET"])
def get_city(city_name):
    doc = cities.document(city_name.strip().lower()).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    return jsonify({"error": "City not found"}), 404

# CREATE
@app.route("/city", methods=["POST"])
def create_city():
    data = request.get_json()
    if not data or not data.get("city"):
        return jsonify({"error": "JSON with 'city' field required"}), 400
    doc_id = data["city"].strip().lower()
    doc_ref = cities.document(doc_id)
    if doc_ref.get().exists:
        return jsonify({"error": "City already exists"}), 409
    doc_ref.set(data)
    return jsonify({"message": "City created", "data": data}), 201

# UPDATE (partial merge)
@app.route("/city/<city_name>", methods=["PUT"])
def update_city(city_name):
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    doc_ref = cities.document(city_name.strip().lower())
    if not doc_ref.get().exists:
        return jsonify({"error": "City not found"}), 404
    doc_ref.set(data, merge=True)  # merge=True does partial update
    return jsonify({"message": "City updated", "data": doc_ref.get().to_dict()}), 200

# DELETE
@app.route("/city/<city_name>", methods=["POST"])
def delete_city(city_name):
    doc_ref = cities.document(city_name.strip().lower())
    if not doc_ref.get().exists:
        return jsonify({"error": "City not found"}), 404
    deleted = doc_ref.get().to_dict()
    doc_ref.delete()
    return jsonify({"message": "City deleted", "data": deleted}), 200

if __name__ == "__main__":
    app.run(debug=True)

