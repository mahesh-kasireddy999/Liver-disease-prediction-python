from flask import Flask, render_template, request, redirect, url_for, session, flash
import joblib
import numpy as np
import os

app = Flask(__name__, template_folder="templates")
app.secret_key = "super_secret_key"

if os.path.exists("users.py"):
    from users import users
else:
    users = {}

@app.route("/")
def home():
    return render_template("home.html", logged_in=session.get("logged_in", False))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if users.get(email) == password:
            session["logged_in"] = True
            session["user"] = email
            return redirect(url_for("home"))
        else:
            flash("Incorrect email or password.")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        users[email] = password
        with open("users.py", "w") as f:
            f.write(f"users = {users}")
        flash("Signup successful. Please login.")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))

@app.route("/liver")
def liver():
    return render_template("liver.html")

def ValuePredictor(to_predict_list, size):
    to_predict = np.array(to_predict_list).reshape(1, size)
    loaded_model = joblib.load("liver_model.pkl")
    result = loaded_model.predict(to_predict)[0]
    prob = loaded_model.predict_proba(to_predict)[0][1]
    disease_type = None

    if prob > 0.60:
        if 0.60 < prob <= 0.65:
            disease_type = "You might have Gilbert's Syndrome"
        elif 0.65 < prob <= 0.70:
            disease_type = "You might have Hemochromatosis"
        elif 0.70 < prob <= 0.75:
            disease_type = "You might have Primary Biliary Cholangitis"
        elif 0.75 < prob <= 0.78:
            disease_type = "You might have Alcoholic Liver Disease"
        elif 0.78 < prob <= 0.81:
            disease_type = "You might have Autoimmune Hepatitis"
        elif 0.81 < prob <= 0.84:
            disease_type = "You might have Non-Alcoholic Fatty Liver Disease (NAFLD)"
        elif 0.84 < prob <= 0.87:
            disease_type = "You might have Hepatitis B"
        elif 0.87 < prob <= 0.90:
            disease_type = "You might have Hepatitis C"
        elif 0.90 < prob <= 0.95:
            disease_type = "You might have Liver Fibrosis"
        elif prob > 0.95:
            disease_type = "You might have advanced Cirrhosis"
        disease_type += ", So please consult a doctor immediately."
    return result, prob, disease_type

@app.route("/predict", methods=["POST"])
def predict():
    if request.method == "POST":
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        to_predict_list = list(map(float, to_predict_list))
        if len(to_predict_list) == 7:
            result, prob, disease_type = ValuePredictor(to_predict_list, 7)
            if int(result) == 1:
                prediction = "⚠️ Sorry, you have chances of getting Inherited Liver Disease."
                if disease_type:
                    prediction += f" We are {round(prob * 100, 2)}% confident that, "
                    prediction += f" {disease_type}"
            else:
                prediction = "✅ No need to fear! You have no dangerous symptoms of the disease."
        return render_template("result.html", prediction_text=prediction)

if __name__ == "__main__":
    app.run(debug=True)
