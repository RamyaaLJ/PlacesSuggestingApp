from flask import Flask, request, jsonify, render_template
import pymongo
import bcrypt
from helper import RestaurantData

app = Flask(__name__, template_folder='.')

# Replace the following with your MongoDB Atlas connection string
MONGO_URI = "mongodb+srv://hemapriya:TgTXMbXyxrnJ4aDJ@cluster0.b933vhr.mongodb.net/?retryWrites=true&w=majority"

# Initialize the MongoDB client
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["user_db"]
users_collection = db["users"]
missing_info_collection = db['missing_info']

options_data = {
    "Option 1": ["Option A", "Option B", "Option C"],
    "Option 2": ["Option D", "Option E", "Option F"],
    "Option 3": ["Option G", "Option H", "Option I"],
}

restaurant = RestaurantData()
    # print(r.ReturnCityName())
    # print(r.ReturnLocalityName('Coimbatore'))
    # print(r.ReturnTopFiveRestaurantName())
@app.route("/")
def home():
    return render_template('home.html')

@app.route("/homepage")
def placesendpoint():
    return render_template("homepage.html")

@app.route("/categories")
def categories():
    return render_template("categories.html")

@app.route("/categories1")
def categories1():
    return render_template("categories1.html")

@app.route("/categories2")
def categories2():
    return render_template("categories2.html")

@app.route("/categories3")
def categories3():
    return render_template("categories3.html")

@app.route("/categories4")
def categories4():
    return render_template("categories4.html")

@app.route("/categories5")
def categories5():
    return render_template("categories5.html")

@app.route("/categories6")
def categories6():
    return render_template("categories6.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/places")
def places():
    return render_template("places.html")

@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")

@app.route("/rating")
def rating():
    return render_template("rating.html")

@app.route("/missing_info", methods=['GET','POST'])
def missing_info():
    if request.method == 'POST':
        data = request.json  # Assuming the data is sent as JSON in the request body

        # Extract shop information from the request
        name = data.get('name')
        area = data.get('area')
        city = data.get('city')
        gmaps_link = data.get('gmaps_link')
        contact = data.get('contact')

        # Create a document for the shop information
        shop_info = {
            'name': name,
            'area': area,
            'city': city,
            'gmaps_link': gmaps_link,
            'contact': contact
        }

        # Insert the document into the "missing_info" collection
        missing_info_collection.insert_one(shop_info)

        return jsonify({'message': 'Shop information stored successfully.'}), 201
    else:
        return render_template('missing_info.html')


@app.route("/register", methods=["GET", "POST"])
def signupuser():
    if request.method == "POST":
        try:
            data = request.get_json()
            fullname = data["name"]
            email = data["email"]
            password = data["password"]

            # Check if the username already exists in the database
            if users_collection.find_one({"username": email}):
                return jsonify({"message": "Username already exists"}), 400

            # Hash the password using bcrypt
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            # Save the user to the database
            user_data = {"username": email, "password": hashed_password}
            users_collection.insert_one(user_data)

            return jsonify({"message": "Signup successful"}), 200

        except Exception as e:
            return jsonify({"message": "Internal server Error", "error": str(e)}), 500

    else:
        return render_template('register.html')


@app.route("/login", methods=["GET", "POST"])
def loginuser():
    if request.method == "POST":
        try:
            data = request.get_json()
            email = data["email"]
            password = data["password"]

            # Retrieve the user from the database
            user_data = users_collection.find_one({"username": email})

            if not user_data:
                return jsonify({"message": "User not found"}), 404

            # Check if the password matches the stored hash using bcrypt
            if bcrypt.checkpw(password.encode("utf-8"), user_data["password"]):
                return jsonify({"message": "Login successful"}), 200

            else:
                return jsonify({"message": "Invalid password"}), 401
            
        except Exception as e:
            return jsonify({"message": "Internal server Error", "error": str(e)}), 500
    else:
        return render_template('login.html')


@app.route("/search", methods=["GET", "POST"])
def searcher():
    if request.method == "GET":
        return render_template('index.html', options=restaurant.ReturnCityName())
    else:
        # try:
            data = request.get_json()
            first_option = data.get("firstOption")
            second_option = data.get("secondOption")
            third_option = data.get("thirdOption")

            # print(restaurant.ReturnList(first_option, second_option, third_option))
            
            return restaurant.ReturnList(first_option, second_option, third_option)
    
@app.route("/get_locality", methods=["POST"])
def get_locality_options():
    data = request.get_json()
    selected_option = data.get("selectedOption")
    options = restaurant.ReturnLocalityName(selected_option)

    return jsonify({"options": options})

@app.route("/get_restaurants", methods=["POST"])
def get_restaurant_options():
    data = request.get_json()
    selected_option = data.get("selectedOption")
    first_option = data.get("firstOption")
    options = restaurant.ReturnRestaurantName(first_option, selected_option)

    return jsonify({"options": options})

if __name__ == "__main__":
    app.run(debug=True)
