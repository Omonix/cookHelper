import cohere, os, dotenv, flask_cors, flask, pymongo, hashlib, time

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
    """Function that authenticity the call for food.
        - Input : - data : call's content - dict
        - Output : return if the call is successfully authenticated - bool"""
    body = "{" + f'"user":"{data.get("user")}","food":"{data.get("food")}","like":{"true" if data.get('like') else "false"}' + "}"
    if time.time() - data.get("time") < 120:
        signature = hashlib.sha256((os.getenv('APP_SECRET') + body + f'{data.get("time")}').encode()).hexdigest()
        if signature == data.get("code"):
            return True
        else:
            print("Wrong code")
            return False
    else:
        print('Later')
        return False
def is_signed_removed(data):
    """Function that authenticity the call for child before is will removed.
        - Input : - data : call's content - dict
        - Output : return if the call is successfully authenticated - bool"""
    body = "{" + f'"name":"{data.get("name")}"' + "}"
    if time.time() - data.get("time") < 120:
        signature = hashlib.sha256((os.getenv("APP_SECRET") + body + f'{data.get("time")}').encode()).hexdigest()
        if signature == data.get("code"):
            return True
        else:
            print("wrong code")
            return False
    else:
        print("Later")
        return False

@app.route("/generate", methods=["GET"], strict_slashes=False)
def gen():
    """Root that generate a recipe with all informations in database.
        - Input : - lang : the return's language - str
        - Output : the response of the AI - str"""
    all_disliked = []
    all_liked = []
    collections = db.list_collection_names()
    for collection in collections:
        disliked = list(db[collection].find({"like": False}))
        liked = list(db[collection].find({"like": True}))
        for e in disliked:
            if e["food"] not in all_disliked:
                all_disliked.append(e["food"])
        for e in liked:
            if e["food"] not in all_liked:
                all_liked.append(e["food"])
    return co.chat(message=f"Find a recipe for {len(collections)} people (answer in {flask.request.args.get("lang")}, without : {all_disliked} and try to prioritize : {all_liked})").text, 201
@app.route("/addfood", methods=["POST"], strict_slashes=False)
def addfood():
    """Root that add a food in database.
        - Input : - data : all infos to verify the call and post the food in database - dict
        - Output : response with message and his code - str, int"""
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
    """Root that removed a child from the database.
        - Input : - data : all informations to verify and delete the child in the database - dict
        - Ouput : response with a message and his code - str, int"""
    data = flask.request.get_json()
    if is_signed_removed(data):
        if data.get("name") in db.list_collection_names():
            db[data.get("name")].drop()
            return f'{data.get("name")} was deleted', 201
        else:
            print("Can't remove child")
            return "Can't remove child", 401
    else:
        print("Can't removed this child")
        return "Can't removed this child", 201

if __name__ == "__main__":
    try:
        print("Server is running ✅")
        app.run(host=URL_API, port=5000, debug=True)
    except:
        print("Error 501 : Can't run server ❌")
