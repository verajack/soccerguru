from flask import Flask, render_template, request
from post import Post
from match import Match
import requests
import json

uri = 'https://api.football-data.org/v4/competitions/ELC/matches?status=FINISHED'
headers = { 'X-Auth-Token': '611a49203eca499a90945814f14d0d8f' }
app = Flask(__name__)

match=[]
@app.route('/')
def show_scores():
    print("Hello")
    count=0
    post_obj=[]
    teams=[]
    response = requests.get(uri, headers=headers)
    for match in response.json()['matches']:
        count=count+1
        # if (match['awayTeam']['name'] == "Sheffield Wednesday FC"):
        post_obj.append(f"{match['homeTeam']['name']} {match['score']['fullTime']['home']} : {match['score']['fullTime']['away']} {match['awayTeam']['name']}")
        if (match['awayTeam']['name'] not in teams ):
            teams.append(f"{match['awayTeam']['name']}")


    return render_template("index.html", all_posts=post_obj, all_teams=teams, counter=count)

@app.route('/teams', methods=['POST'])
def show_team_scores():
    print("Hello")
    count=0
    post_obj=[]
    teams=[]
    response = requests.get(uri, headers=headers)
    name = request.form["teamlist"]
    for match in response.json()['matches']:
        count=count+1
        if (match['awayTeam']['name'] == name) or (match['homeTeam']['name'] == name):
            post_obj.append(f"{match['homeTeam']['name']} {match['score']['fullTime']['home']} : {match['score']['fullTime']['away']} {match['awayTeam']['name']}")
        teams.append(f"{match['awayTeam']['name']}")


    return render_template("index.html", all_posts=post_obj, all_teams=teams, counter=count)

if __name__ == "__main__":
    app.run(debug=True)


