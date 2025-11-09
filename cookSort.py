import cohere, os, dotenv, flask_cors, flask, pymongo, hmac, hashlib, base64, time, json

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

def is_signed_food(data):
    body = "{" + f'"user":"{data["user"]}","food":"{data["food"]}","like":{"true" if data['like'] else "false"}' + "}"
    if time.time() - data["time"] < 120:
        signature = hashlib.sha256((os.getenv('APP_SECRET') + body + f'{data["time"]}').encode()).hexdigest()
        if signature == data.get("code"):
            return True
        else:
            print("Wrong code")
            return False
    else:
        print('Later')
        return False
@app.route("/generate", methods=["GET"], strict_slashes=False)
def gen():
    return co.chat(message=f'Find a recipe (response in {flask.request.args.get("lang")})').text, 201
@app.route("/addfood", methods=["POST"], strict_slashes=False)
def addfood():
    data = flask.request.get_json()
    if is_signed_food(data):
        try:
            user_selected = db[data.get("user")]
            if user_selected.find_one({"food": data.get("food")}):
                user_selected.update_one({"food": data.get("food")}, {"$set": {"like": data.get("like")}})
                return f"{data.get("user")} was successfully added", 201
            else:
                new_data = {'food': data.get("food"), 'like': data.get("like")}
                user_selected.insert_one(new_data)
                return f"{data.get("user")} was successfully added", 201
        except:
            print("Can't add ingredient")
            return "Can't add ingredient", 401
    else:
        print("Can't add ingredient")
        return "Can't add ingredient", 401
@app.route('/removechild', methods=["POST"], strict_slashes=False)
def removechild():
    data = flask.request.get_json()
    if data.get("name") in db.list_collection_names():
        db[data.get("name")].drop()
        return f'{data.get("name")} was deleted', 201
    else:
        print("Can't remove child")
        return "Can't remove child", 401

if __name__ == "__main__":
    try:
        print("Server is running ✅")
        app.run(host=URL_API, port=5000, debug=True)
    except:
        print("Error 501 : Can't run server ❌")
