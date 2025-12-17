from flask import Flask, render_template, request, redirect, session
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "danchilka_secret"
app.permanent_session_lifetime = timedelta(days=7)

# TEMP STORAGE
users = {}
donations = []

# HOME
@app.route("/")
def home():
    email = session.get("user")

    if email and email in users:
        return render_template(
            "index.html",
            user_name=users[email]["name"]
        )

    # session exists but user data missing → logout safely
    session.pop("user", None)
    return render_template("index.html")

# SIGN UP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]

        if email in users:
            return "Account already exists"

        users[email] = {
            "name": request.form["name"],
            "dob": request.form["dob"],
            "phone": request.form.get("phone"),
            "password": request.form["password"]
        }

        return redirect("/login")

    return render_template("signup.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email in users and users[email]["password"] == password:
            session["user"] = email        # ✅ store logged-in user
            session.permanent = True       # ✅ keep session for 7 days
            return redirect("/")

        return "Invalid login"

    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    email = session.get("user")

    # 🔒 Full safety check
    if not email or email not in users:
        session.pop("user", None)
        return redirect("/login")

    # Ensure profile exists
    users[email].setdefault("profile", {})

    if request.method == "POST":

        # Save owner & organisation ONLY ONCE
        if "owner_name" not in users[email]["profile"]:
            users[email]["profile"] = {
                "owner_name": request.form["owner_name"],
                "org_name": request.form["org_name"]
            }

        donation = {
            "email": email,
            "address": request.form["address"],
            "quantity": request.form["quantity"],
            "collection_time": request.form["collection_time"],
            "pickup_time": request.form["pickup_time"],
            "drop_time": request.form["drop_time"],
        }

        donations.append(donation)
        return redirect("/dashboard")

    return render_template(
    "dashboard.html",
    user_name=users[email]["name"],
    profile=users[email]["profile"],
    donations=[d for d in donations if d["email"] == email]
)

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run()
