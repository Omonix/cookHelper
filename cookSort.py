import cohere, os, dotenv, flask_cors, flask, pymongo

def to_json(doc):
    doc["_id"] = str(doc["_id"])
    return doc

dotenv.load_dotenv()
AI_KEY = os.getenv('AI_KEY')
DB_KEY = os.getenv('DB_KEY')
URL_API = os.getenv('URL_API')
app = flask.Flask(__name__)
flask_cors.CORS(app)

try:
    co = cohere.Client(AI_KEY)
    print("Connected to AI ✅")
except:
    print("Error 501 : Can't connect to AI API ❌")
try:
    client = pymongo.MongoClient(DB_KEY)
    print("Connected to Data Base ✅")
except:
    print("Error 501 : Can't connect to Data Base ❌")

db = client["childs"]
#user1 = db["user1"]

@app.route("/food", methods=["POST"], strict_slashes=False)
def food():
    data = flask.request.get_json()
    user_selected = db[data.get("user")]
    new_data = {'food': data.get("food"), 'like': data.get("like")}
    result = user_selected.insert_one(new_data)
    return flask.jsonify({"_id": str(result.inserted_id)}), 201

if __name__ == "__main__":
    try:
        print("Server is running ✅")
        app.run(host=URL_API, port=5000, debug=True)
    except:
        print("Error 501 : Can't run server ❌")
#print(co.chat(message='Quel jour sommes nous').text)
