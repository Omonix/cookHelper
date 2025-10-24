import cohere, os, dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId

def to_json(doc):
    doc["_id"] = str(doc["_id"])
    return doc

dotenv.load_dotenv()
AI_KEY = os.getenv('AI_KEY')
DB_KEY = os.getenv('DB_KEY')
app = Flask(__name__)
CORS(app)
try:
    co = cohere.Client(AI_KEY)
    print("Connected to AI ✅")
except:
    print("Error 501 : Can't connect to AI API ❌")
try:
    client = MongoClient(DB_KEY)
    print("Connected to Data Base ✅")
except:
    print("Error 501 : Can't connect to Data Base ❌")
if __name__ == "__main__":
    try:
        print("Server is running ✅")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except:
        print("Error 501 : Can't run server ❌")
#print(co.chat(message='Quel jour sommes nous').text)
db = client["childs"]
louis = db["louis"]
#anais = db["anais"]
#juliette = db["juliette"]
#this_food = {"food": "steak", "like": True}
#louis.insert_one(this_food)

@app.route("/food", methods=["POST"])
def add_food():
    data = request.get_json()
    result = louis.insert_one(data)
    return jsonify({"_id": str(result.inserted_id)}), 201
