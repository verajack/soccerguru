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
    homeForm={}
    awayForm={}
    form={}
    name=""

    response = requests.get(uri, headers=headers)
    for match in response.json()['matches']:
        count=count+1
        # if (match['awayTeam']['name'] == "Sheffield Wednesday FC"):
        post_obj.append(f"{match['homeTeam']['name']} {match['score']['fullTime']['home']} : {match['score']['fullTime']['away']} {match['awayTeam']['name']}")
        #new_item = f"{match['awayTeam']['name']} : {match['score']['fullTime']['home']}"
        #print(new_item)
        #item_id = todo_db.addMany(response.json()['matches'])
        #print(item_id)
        homeTeam = str(match['homeTeam']['name'])
        print(f"Hometeam is {homeTeam}")
        awayTeam = str(match['awayTeam']['name'])
        print(f"AwayTeam is {awayTeam}")

        if(match['score']['fullTime']['home']) > (match['score']['fullTime']['away']):

            if homeTeam not in homeForm.keys():
                homeForm[homeTeam] = "W"
            else:
                homeForm[homeTeam] += "W"

            if homeTeam not in form.keys():
                form[homeTeam] = "W"
            else:
                print(f"{homeTeam}  in form.keys ")
                form[homeTeam] += "W"

            if awayTeam not in awayForm.keys():
                awayForm[awayTeam] = "L"
            else:
                awayForm[awayTeam] += "L"

            if awayTeam not in form.keys():
                form[awayTeam] = "L"
            else:
                form[awayTeam] += "L"

        elif(match['score']['fullTime']['home']) < (match['score']['fullTime']['away']):

            if homeTeam not in homeForm.keys():
                homeForm[homeTeam] = "L"
            else:
                homeForm[homeTeam] += "L"

            if homeTeam not in form.keys():
                form[homeTeam] = "L"
            else:
                print(f"{homeTeam}  in form.keys ")
                form[homeTeam] += "L"

            if awayTeam not in awayForm.keys():
                awayForm[awayTeam] = "W"
            else:
                awayForm[awayTeam] += "W"

            if awayTeam not in form.keys():
                form[awayTeam] = "W"
            else:
                form[awayTeam] += "W"

        elif(match['score']['fullTime']['home']) == (match['score']['fullTime']['away']):

            if homeTeam not in homeForm.keys():
                homeForm[homeTeam] = "D"
            else:
                homeForm[homeTeam] += "D"

            if homeTeam not in form.keys():
                form[homeTeam] = "D"
            else:
                print(f"{homeTeam}  in form.keys ")
                form[homeTeam] += "D"

            if awayTeam not in awayForm.keys():
                awayForm[awayTeam] = "D"
            else:
                awayForm[awayTeam] += "D"

            if awayTeam not in form.keys():
                form[awayTeam] = "D"
            else:
                form[awayTeam] += "D"

        print(form)





        if (match['awayTeam']['name'] not in teams ):
            teams.append(f"{match['awayTeam']['name']}")
    teams.sort()
    print(form)

    json_object = json.dumps(form, indent=4)
    with open("form.json", "w") as outfile:
        outfile.write(json_object)

    json_object = json.dumps(homeForm, indent=4)
    with open("homeForm.json", "w") as outfile:
        outfile.write(json_object)

    json_object = json.dumps(awayForm, indent=4)
    with open("awayForm.json", "w") as outfile:
        outfile.write(json_object)




    return render_template("index.html", all_posts=post_obj, all_teams=teams,form=form, counter=count)

@app.route('/teams', methods=['POST'])
def show_team_scores():
    print("Hello")
    count=0
    post_obj=[]
    teams=[]
    homeForm={}
    awayForm={}
    form={}
    response = requests.get(uri, headers=headers)
    name = request.form["teamlist"]
    for match in response.json()['matches']:
        count=count+1
        if (match['awayTeam']['name'] == name) or (match['homeTeam']['name'] == name):
            post_obj.append(f"{match['homeTeam']['name']} {match['score']['fullTime']['home']} : {match['score']['fullTime']['away']} {match['awayTeam']['name']}")
        if (match['awayTeam']['name'] not in teams ):
            teams.append(f"{match['awayTeam']['name']}")
    teams.sort()

    return render_template("index.html", all_posts=post_obj, all_teams=teams,form=form, counter=count, selectedTeam=name)

if __name__ == "__main__":
    app.run(debug=True)


