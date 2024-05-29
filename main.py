from flask import Flask, render_template, request
from post import Post
from match import Match
import requests
import json
from pysondb import getDb
todo_db = getDb('todo.json')

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
    form={}

    response = requests.get(uri, headers=headers)
    for match in response.json()['matches']:
        count=count+1
        # if (match['awayTeam']['name'] == "Sheffield Wednesday FC"):
        post_obj.append(f"{match['homeTeam']['name']} {match['score']['fullTime']['home']} : {match['score']['fullTime']['away']} {match['awayTeam']['name']}")
        #new_item = f"{match['awayTeam']['name']} : {match['score']['fullTime']['home']}"
        #print(new_item)
        #item_id = todo_db.addMany(response.json()['matches'])
        #print(item_id)
        if(match['score']['fullTime']['home']) > (match['score']['fullTime']['away']):

            homeTeam = str(match['homeTeam']['name'])
            if(homeTeam not in form.keys()):
                form[homeTeam] = "W"
            else:
                form[homeTeam] += "W"
        elif(match['score']['fullTime']['home']) < (match['score']['fullTime']['away']):
            homeTeam = str(match['homeTeam']['name'])
            if(homeTeam not in form.keys()):
                form[homeTeam] = "L"
            else:
                form[homeTeam] += "L"
        elif(match['score']['fullTime']['home']) == (match['score']['fullTime']['away']):
            homeTeam = str(match['homeTeam']['name'])
            if(homeTeam not in form.keys()):
                form[homeTeam] = "D"
            else:
                form[homeTeam] += "D"
        print(form)





        if (match['awayTeam']['name'] not in teams ):
            teams.append(f"{match['awayTeam']['name']}")
    teams.sort()
    print(form)


    return render_template("index.html", all_posts=post_obj, all_teams=teams,form=form, counter=count)

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
        if (match['awayTeam']['name'] not in teams ):
            teams.append(f"{match['awayTeam']['name']}")
    teams.sort()

    return render_template("index.html", all_posts=post_obj, all_teams=teams, counter=count)

if __name__ == "__main__":
    app.run(debug=True)


