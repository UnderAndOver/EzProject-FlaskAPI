from flask import Flask, jsonify, request, abort, g
from flask_pymongo import PyMongo
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from validate_email import validate_email
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'
app.config['SECRET_KEY']= b'{\x90\xaa, =9z\xb1\x0c:\x1f\xb6\x12\x83\xbe\xae\xca#\x12\xdc\x9b\xb1Y'
app.secret_key= b'{\x90\xaa, =9z\xb1\x0c:\x1f\xb6\x12\x83\xbe\xae\xca#\x12\xdc\x9b\xb1Y'
mongo = PyMongo(app)
TOKEN_EXPIRATION=2678400

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)

jwt = Serializer(app.config['SECRET_KEY'], TOKEN_EXPIRATION) #1 month token
@app.route('/register', methods= ['POST'])
def register():
    g.user = None
    email = request.json['email']
    password = request.json['password']
    users = mongo.db.customers
    if email is None or password is None:
        return 'invalid entry'
    if validate_email(email) is False:
        return 'invalid email'
    if len(password)<8:
        return 'password must at least have 8 characters'
    if users.find({'email': {"$in":[email]}}).limit(1).count()==0:
        users.insert({'email':email, 'password':generate_password_hash(password)})
        user_id_json=users.find_one({"email":email},{"_id":1})
        users.update({'email':email}, {'$set':{'customer_id':str(user_id_json.get('_id'))}})
        token = generate_token(str(user_id_json.get("_id")))
        return jsonify({'token': token.decode('ascii'), '_id':str(user_id_json.get('_id'))})
    else:
        return 'user already in db'



@basic_auth.verify_password
def verify_password(email, password):
    g.user = None
    cursor = mongo.db.customers.find({"email": {"$exists": 1}}).limit(1)
    if cursor.count()>0:
        user=mongo.db.customers.find_one({"email":email},{"password":1, "_id":0})
        if check_password_hash(user.get("password"), password):
            g.user = mongo.db.customers.find_one({"email":email}, {"customer_id":1, "_id":0})
            g.user = g.user.get("customer_id")
            return True
    return False

def generate_token(id):
    return jwt.dumps({'_id':id}) #turning objectid to string form for value
@token_auth.verify_token
def verify_token(token):
    users = mongo.db.customers
    g.user = None
    tup= validate_token(token)
    id = tup[2]
    for user in users.find():
        if str(user.get("_id")) == id :
            g.user=tup[2]
            return True
    return False

def validate_token(user_token):
    s=Serializer(app.config['SECRET_KEY'], TOKEN_EXPIRATION)
    try:
        data = s.loads(user_token)
        is_valid = True
        has_expired = False
        id = data.get('_id') #token already has value in string form
    except SignatureExpired:
        is_valid = False
        has_expired = True
        id = None
    except BadSignature:
        is_valid = False
        has_expired = False
        id = None
    return (is_valid, has_expired, id)

@app.route('/items')
@multi_auth.login_required
def get_items_list():
    items = mongo.db.items
    item_list= []
    for item in items.find():
        item.pop('_id')
        item_list.append(item)
    return jsonify(item_list) #maybe make json object with item_list=item_list

@app.route('/orders')
@multi_auth.login_required
def get_order():
    #input =({"email":request.values.get("email"),
    # "password":request.values.get("password")})
    customers = mongo.db.customers
    customer_id = g.user
    orders = mongo.db.orders
    order_list=[]
    for order in orders.find({"customer_id":customer_id}):
        order.pop('_id')
        order_list.append(order)
    return jsonify(order_list)

@app.route('/orders' , methods=['POST'])
@multi_auth.login_required
def create_order():
    customers = mongo.db.customers
    customer_id = g.user
    orders = mongo.db.orders
    items = {}
    for item in request.json['items']:
        items[item.get('item_id')]=item.get('amount')
    orders.insert({"customer_id":customer_id})
    for k,v in items.items():
        orders.update({"customer_id":customer_id}, {"$set":{"items":{"item_id":k, "amount":v}}})
    return "SUCCESS"










if __name__ == '__main__':
    app.run(debug=True)