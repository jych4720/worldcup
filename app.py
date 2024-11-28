from flask import Flask, render_template, request
import re
import requests
from datetime import datetime
app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    input_name = request.form.get("name")
    input_age = request.form.get("age")
    input_year = request.form.get('bornyear')
    return render_template("hello.html", name=input_name,
                           age=input_age, bornyear=input_year)


def process_query(query):
    if query == "dinosaurs":
        return "Dinosaurs ruled the Earth 200 million years ago"
    elif query == "asteroids":
        return "Unknown"
    elif query == "What is your name?":
        return "jc4720"
    match = re.match(r"What is (\d+) plus (\d+)\?", query)
    if match:
        # Extract the numbers and calculate the sum
        num1 = int(match.group(1))
        num2 = int(match.group(2))
        result = num1 + num2
        return str(result)
    match_largest = re.match(
        r"Which of the following numbers is the largest: ([\d, ]+)\?", query
    )
    if match_largest:
        numbers = list(map(int, match_largest.group(1).split(',')))
        largest_number = max(numbers)
        return str(largest_number)
    match_multiplication = re.match(
        r"What is (\d+) multiplied by (\d+)\?", query)
    if match_multiplication:
        num1 = int(match_multiplication.group(1))
        num2 = int(match_multiplication.group(2))
        result = num1 * num2
        return str(result)
    match_subtraction = re.match(r"What is (\d+) minus (\d+)\?", query)
    if match_subtraction:
        num1 = int(match_subtraction.group(1))
        num2 = int(match_subtraction.group(2))
        result = num1 - num2
        return str(result)
    match_exponentiation = re.match(
        r"What is (\d+) to the power of (\d+)\?", query)
    if match_exponentiation:
        base = int(match_exponentiation.group(1))
        exponent = int(match_exponentiation.group(2))
        result = base ** exponent  # Calculate power
        return str(result)
    return "Unknown"


@app.route("/query", methods=["GET"])
def query():
    query_param = request.args.get('q')
    if query_param:
        result = process_query(query_param)
    else:
        result = "Query parameter 'q' is missing."
    return result


@app.route("/submit_github", methods=["POST"])
def submit_github():
    input_username = request.form.get("username")
    url = (
        f"https://api.github.com/users/{input_username}/repos"
    )
    response = requests.get(url)
    repos = []
    if response.status_code == 200:
        repos = response.json()
        for repo in repos:
            repo['updated_at'] = datetime.strptime(
                repo['updated_at'], "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%B %d, %Y at %I:%M %p")
    followers_url = f"https://api.github.com/users/{input_username}/followers"
    followers_response = requests.get(followers_url)
    followers = []
    if followers_response.status_code == 200:
        followers = followers_response.json()
    return render_template("hello2.html", username=input_username,
                           repos=repos, followers=followers)
