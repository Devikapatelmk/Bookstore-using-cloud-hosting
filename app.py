from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "secret123"

# -------- MONGODB SETUP --------
MONGO_URI = "mongodb+srv://devikapatelmk_db_user:devika%402005@cluster0.pkzijxg.mongodb.net/bookstore_db?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["bookstore_db"]
books_col = db["books"]
users_col = db["users"]
booking_col = db["bookings"]

# -------- ROUTES --------
@app.route("/")
def home():
    books = list(books_col.find())
    return render_template("home.html", books=books)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if users_col.find_one({"username": username}):
            flash("Username already exists!", "warning")
            return redirect(url_for("register"))
        if users_col.find_one({"email": email}):
            flash("Email already registered!", "warning")
            return redirect(url_for("register"))

        users_col.insert_one({
            "username": username,
            "email": email,
            "password": password
        })
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users_col.find_one({"username": username, "password": password})
        if user:
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))

@app.route("/book/<int:book_id>")
def book_details(book_id):
    book = books_col.find_one({"_id": book_id})
    return render_template("book_details.html", book=book)

@app.route("/booking/<int:book_id>", methods=["GET", "POST"])
def booking(book_id):
    book = books_col.find_one({"_id": book_id})

    if not book:
        flash("Book not found!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        if "user_id" not in session:
            flash("Please login to book a book.", "warning")
            return redirect(url_for("login"))

        booking_col.insert_one({
            "user_id": session["user_id"],
            "book_id": book_id,
            "status": "Pending"
        })
        flash(f"Booking for '{book['title']}' confirmed!", "success")
        return redirect(url_for("home"))

    return render_template("booking.html", book=book)

# -------- RUN APP --------
if __name__ == "__main__":
    app.run(debug=True)
