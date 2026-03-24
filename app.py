from flask import Flask, render_template
import numpy as np
from sklearn.linear_model import LogisticRegression
import requests
import random
from datetime import datetime

app = Flask(__name__)

# -------------------------------
# TRAINING DATA (SIMULATED)
# -------------------------------
X = np.array([
    [1, 6],
    [2, 5],
    [3, 2],
    [5, 1],
    [4, 2],
    [1, 7],
    [2, 6],
    [5, 0],
    [3, 1]
])

y = np.array([1,1,0,0,0,1,1,0,0])

model = LogisticRegression()
model.fit(X, y)

# -------------------------------
# RECOMMENDATIONS FUNCTION
# -------------------------------
def get_recommendations(genre):
    genre_mapping = {
        "Thriller": "horror",
        "Action": "action",
        "Drama": "drama",
        "Comedy": "comedy",
        "Romance": "romance"
    }

    api_genre = genre_mapping.get(genre, genre.lower())

    fallback_recommendations = {
        "horror": ["The Conjuring", "Insidious", "The Ring"],
        "action": ["John Wick", "Mad Max Fury Road", "Deadpool"],
        "drama": ["The Shawshank Redemption", "Forrest Gump", "The Pursuit of Happiness"],
        "comedy": ["Superbad", "The Hangover", "Bridesmaids"],
        "romance": ["The Notebook", "Titanic", "Pride and Prejudice"]
    }

    try:
        response = requests.get(f"https://api.sampleapis.com/movies/{api_genre}", timeout=5)
        if response.status_code == 200:
            movies = response.json()
            recommendations = [
                movie.get("title", movie.get("name", "Unknown"))
                for movie in movies[:3]
            ]
            return recommendations if recommendations else fallback_recommendations.get(api_genre)
    except:
        pass

    return fallback_recommendations.get(api_genre, ["Movie 1", "Movie 2", "Movie 3"])

# -------------------------------
# DYNAMIC USERS FUNCTION
# -------------------------------
def fetch_dynamic_users():
    genres = ["Action", "Thriller", "Drama", "Comedy", "Romance"]
    platforms_list = [
        ["Netflix", "Prime", "Hotstar"],
        ["Netflix", "Netflix", "Netflix"],
        ["Netflix", "Prime"],
        ["Netflix", "Netflix"],
        ["Netflix", "Disney+"]
    ]

    try:
        # ✅ UPDATED: Indian users only
        response = requests.get("https://randomuser.me/api/?results=5&nat=in", timeout=5)

        if response.status_code == 200:
            api_users = response.json().get("results", [])
            users = []

            for user in api_users:
                users.append({
                    "name": f"{user['name']['first'].capitalize()} {user['name']['last'].capitalize()}",
                    "frequency": random.randint(1, 5),
                    "days": random.randint(0, 7),
                    "genre": random.choice(genres),
                    "platforms": random.choice(platforms_list)
                })

            return users if users else fallback_users()

    except:
        pass

    return fallback_users()


def fallback_users():
    return [
        {"name": "Rahul Kumar", "frequency": 1, "days": 6, "genre": "Thriller", "platforms": ["Netflix", "Prime", "Hotstar"]},
        {"name": "Aman Singh", "frequency": 3, "days": 2, "genre": "Action", "platforms": ["Netflix", "Netflix", "Netflix"]},
        {"name": "Neha Sharma", "frequency": 5, "days": 1, "genre": "Drama", "platforms": ["Netflix", "Prime"]},
        {"name": "Priya Patel", "frequency": 2, "days": 5, "genre": "Comedy", "platforms": ["Netflix", "Netflix"]},
        {"name": "Vikram Chopra", "frequency": 4, "days": 3, "genre": "Romance", "platforms": ["Netflix", "Disney+"]}
    ]

# -------------------------------
# SERVER TIME FUNCTION
# -------------------------------
def get_server_time():
    try:
        response = requests.get("http://worldtimeapi.org/api/timezone/Asia/Kolkata", timeout=5)
        if response.status_code == 200:
            data = response.json()
            datetime_str = data.get("datetime", "")
            if datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace("+05:30", ""))
                return dt.strftime("%b %d, %Y %I:%M %p IST")
    except:
        pass

    return datetime.now().strftime("%b %d, %Y %I:%M %p IST")

# -------------------------------
# USERS
# -------------------------------
users = fetch_dynamic_users()

# -------------------------------
# AI ANALYSIS
# -------------------------------
def analyze_user(user):
    freq = user["frequency"]
    days = user["days"]

    prob = model.predict_proba([[freq, days]])[0][1] * 100

    if prob > 70:
        risk = "High"
    elif prob > 40:
        risk = "Medium"
    else:
        risk = "Low"

    if prob > 70:
        before = "User likely to churn within a few days"
        after = "User retained through targeted offer and content"
    elif prob > 40:
        before = "User engagement dropping gradually"
        after = "User re-engaged with recommendations"
    else:
        before = "User stable"
        after = "User continues without intervention"

    if len(set(user["platforms"])) > 1:
        behaviour = "Rotational Behaviour"
    else:
        behaviour = "Stable Behaviour"

    if days > 5:
        reason = "User inactivity"
    elif freq < 2:
        reason = "Low engagement"
    else:
        reason = "Healthy usage"

    key_factors = []
    if days > 5:
        key_factors.append("High inactivity")
    if freq < 2:
        key_factors.append("Low engagement")

    if risk == "High":
        action = "Offer ₹99 Weekend Plan"
    elif risk == "Medium":
        action = "Send engagement notification"
    else:
        action = "No action required"

    recommendations = get_recommendations(user['genre'])

    return {
        "name": user["name"],
        "prob": round(prob, 1),
        "risk": risk,
        "reason": reason,
        "factors": key_factors,
        "impact_before": before,
        "impact_after": after,
        "behaviour": behaviour,
        "days": user["days"],
        "genre": user["genre"],
        "action": action,
        "recommendations": recommendations
    }

# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def dashboard():
    analyzed_users = [analyze_user(u) for u in users]
    server_time = get_server_time()
    return render_template("index.html", users=analyzed_users, server_time=server_time)

@app.route("/user/<name>")
def user_detail(name):
    for u in users:
        if u["name"] == name:
            data = analyze_user(u)
            return render_template("user.html", user=data)

# -------------------------------
# RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)