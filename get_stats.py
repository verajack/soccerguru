def get_stats(league_name):
    print(f"League is {league_name}")
    from datetime import datetime
    import json
    import requests

    # uri = 'https://api.football-data.org/v4/competitions/ELC/matches?status=FINISHED'
    uri = f'https://api.football-data.org/v4/competitions/{league_name}/matches?status=FINISHED'
    headers = { 'X-Auth-Token': '611a49203eca499a90945814f14d0d8f' }
    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

    print("Hello")
    count=0
    results=[]
    teams=[]
    homeForm={}
    awayForm={}
    form={}
    name=""

    response = requests.get(uri, headers=headers)
    for match in response.json()['matches']:
        count=count+1
        homeTeam = str(match['homeTeam']['name'])
        #print(f"Hometeam is {homeTeam}")
        awayTeam = str(match['awayTeam']['name'])
        #print(f"AwayTeam is {awayTeam}")
        # if (match['awayTeam']['name'] == "Sheffield Wednesday FC"):
        results.append(f"{match['homeTeam']['name']} {match['score']['fullTime']['home']} : {match['score']['fullTime']['away']} {match['awayTeam']['name']}")

        #new_item = f"{match['awayTeam']['name']} : {match['score']['fullTime']['home']}"
        #print(new_item)
        #item_id = todo_db.addMany(response.json()['matches'])
        #print(item_id)


        if(match['score']['fullTime']['home']) > (match['score']['fullTime']['away']):

            if homeTeam not in homeForm.keys():
                homeForm[homeTeam] = "W"
            else:
                homeForm[homeTeam] += "W"

            if homeTeam not in form.keys():
                form[homeTeam] = "W"
            else:
                #print(f"{homeTeam}  in form.keys ")
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
                #print(f"{homeTeam}  in form.keys ")
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
                #print(f"{homeTeam}  in form.keys ")
                form[homeTeam] += "D"

            if awayTeam not in awayForm.keys():
                awayForm[awayTeam] = "D"
            else:
                awayForm[awayTeam] += "D"

            if awayTeam not in form.keys():
                form[awayTeam] = "D"
            else:
                form[awayTeam] += "D"

        #print(form)

        if (match['awayTeam']['name'] not in teams ):
            teams.append(f"{match['awayTeam']['name']}")
            print("APPENDING TEAMS!")
        else:
            print(f"{match['awayTeam']['name']} not in teams")

        teams.sort()

    with open(f'stats/teams_{league_name}.txt', 'w') as f:
        for line in teams:
            f.write(f"{line}\n")

    with open(f'stats/results_{league_name}.txt', 'w') as f:
        for line in results:
            f.write(f"{line}\n")

    with open(f'stats/team_form_{league_name}.json', 'w') as fp:
        json.dump(homeForm, fp, indent=4)

    with open(f'stats/home_form_{league_name}.json', 'w') as fp:
        json.dump(homeForm, fp, indent=4)

    with open(f'stats/away_form_{league_name}.json', 'w') as fp:
        json.dump(awayForm, fp, indent=4)


leagues = ('PL','ELC')
for league in leagues:
    get_stats(league)

