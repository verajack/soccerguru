import sqlite3

from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import requests
from datetime import datetime
import json
import re
import sqlite3

match = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE TABLE
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


# Function to calculate points from the form
def calculate_points(form):
    points = 0
    for result in form:
        if result == 'W':
            points += 3
        elif result == 'D':
            points += 1
        # Loss (L) contributes 0 points, so we skip it
    return points


# Function to process and sort the dictionary
def process_teams(teams_form, form_history):
    # Slice the form to only include the last `form_history` results
    processed_teams = {
        team: form[-form_history:] for team, form in teams_form.items()
    }

    # Sort the dictionary by points based on the sliced form
    sorted_teams = dict(sorted(
        processed_teams.items(),
        key=lambda x: calculate_points(x[1]),
        reverse=True
    ))

    return sorted_teams


# Function to parse matches
def parse_matches(match_list):
    matches = []
    for match in match_list:
        parts = match.split(" on ")
        teams = parts[0].split(" versus ")
        match_date = parts[1] if len(parts) > 1 else "Unknown Date"
        matches.append((teams[0].strip(), teams[1].strip(), match_date))
    return matches


# Sample team stats dictionary
team_stats = {
    "STOKE CITY FC": {"Wins": 8, "Losses": 6, "Draws": 4, "Points": 28},
    "SUNDERLAND AFC": {"Wins": 10, "Losses": 5, "Draws": 3, "Points": 33},
    "SWANSEA CITY AFC": {"Wins": 7, "Losses": 7, "Draws": 4, "Points": 25},
    "LUTON TOWN FC": {"Wins": 6, "Losses": 8, "Draws": 4, "Points": 22},
    "WATFORD FC": {"Wins": 9, "Losses": 5, "Draws": 4, "Points": 31},
    "CARDIFF CITY FC": {"Wins": 7, "Losses": 6, "Draws": 5, "Points": 26},
    "DERBY COUNTY FC": {"Wins": 8, "Losses": 7, "Draws": 3, "Points": 27},
    "LEEDS UNITED FC": {"Wins": 11, "Losses": 4, "Draws": 3, "Points": 36},
    "MIDDLESBROUGH FC": {"Wins": 10, "Losses": 6, "Draws": 2, "Points": 32},
    "BURNLEY FC": {"Wins": 12, "Losses": 3, "Draws": 3, "Points": 39},
}


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        email = request.form.get('email')
        result = db.session.execute(db.select(User).where(User.email == email))

        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        if user:
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            password=hash_and_salted_password,
            name=request.form.get('name'),
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("secrets"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('secrets'))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    print(current_user.name)
    league_name = "PL"

    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

    with open(f'stats/results_{league_name}.txt') as f:
        results = f.read().splitlines()

    with open(f'stats/teams_{league_name}.txt') as f:
        teams = f.read().splitlines()

    with open(f"stats/team_form_{league_name}.json") as file:
        form = json.load(file)

    # sorted_form = dict(sorted(form.items()))

    return render_template("welcome_page.html", name=current_user.name, logged_in=True, all_posts=results,
                           all_teams=teams, form=form, current_month=current_month_text, current_day=current_day,
                           current_year=current_year_full, current_league="PL")


@app.route('/teams', methods=['POST'])
def show_team_scores():
    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

    count = 0
    post_obj = []
    teams = []
    homeForm = {}
    awayForm = {}
    form = {}
    name = ""

    name = request.form["teamlist"]
    c_league = request.form.get("league_name")
    if c_league == "ELC":
        league_name = "ELC"
    else:
        league_name = "PL"

    league_logo = f"{league_name}.jpg"

    with open(f'stats/results_{league_name}.txt') as f:
        results = f.read().splitlines()

    with open(f'stats/teams_{league_name}.txt') as f:
        teams = f.read().splitlines()

    with open(f'stats/team_form_{league_name}.json') as file:
        form = json.load(file)

    for match in results:
        # if re.search(f"{name}\s+\d+\s+\:", match):
        if re.search(f"{name}", match):
            post_obj.append(match)
        else:
            print(f"{name} not found in {match}")

    # teams.sort()
    # sorted_form = dict(sorted(form.items()))

    return render_template("main_football_page.html", all_posts=post_obj, all_teams=teams, form=form,
                           current_league=league_name, counter=count, league_logo=league_logo,
                           selectedTeam=name, current_month=current_month_text, current_day=current_day,
                           current_year=current_year_full)


@app.route('/form_tables', methods=["GET", "POST"])
def show_form_tables():
    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

    count = 0
    post_obj = []
    teams = []
    homeForm = {}
    awayForm = {}
    form = {}
    name = ""

    league_text = request.form.get("league_name", default="English Premiership")
    form_type = request.form.get("form_type", default="all_form")

    if league_text == "English Championship":
        league_name = "ELC"
    else:
        league_name = "PL"

    league_logo = f"{league_name}.png"

    print(f"League name is {league_name}")

    print(f'League of gents is {league_name}')

    with open(f'stats/results_{league_name}.txt') as f:
        results = f.read().splitlines()

    with open(f'stats/teams_{league_name}.txt') as f:
        teams = f.read().splitlines()

    with open(f'stats/home_form_{league_name}.json') as file:
        home_form = json.load(file)

    with open(f'stats/away_form_{league_name}.json') as file:
        away_form = json.load(file)

    with open(f'stats/team_form_{league_name}.json') as file:
        teams_form = json.load(file)

    games_played = len(teams_form)

    if form_type == "all_form":
        form_history = int(request.form.get("form_history", default=5))
        sorted_form = process_teams(teams_form, form_history)
    elif form_type == "home_form":
        form_history = int(request.form.get("form_history", default=5))
        sorted_form = process_teams(home_form, form_history)
    elif form_type == "away_form":
        form_history = int(request.form.get("form_history", default=5))
        sorted_form = process_teams(away_form, form_history)

    print(f"Form type is {form_type}")
    print(f"Form history is {form_history}")

    form_text = f"Displaying {form_type.replace('_form', '')} games for the last {form_history} matches from the {league_text}"

    print(form_text)

    # sorted_form = dict(sorted(form.items(), key=lambda x: calculate_points(x[1]), reverse=True))
    # Sort the dictionary based on the calculated points
    # Process and sort the teams

    return render_template("form_tables.html", form=sorted_form,
                           league_logo=league_logo, form_history=form_history, form_text=form_text,
                           form_type=form_type, games_played=games_played,
                           current_league=league_name, counter=count,
                           current_month=current_month_text, current_day=current_day,
                           current_year=current_year_full)


@app.route('/fixtures', methods=["GET", "POST"])
def fixtures():
    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

    count = 0
    post_obj = []
    teams = []
    homeForm = {}
    awayForm = {}
    form = {}
    name = ""

    league_text = request.form.get("league_name", default="English Premiership")

    if league_text == "English Championship":
        league_name = "ELC"
    else:
        league_name = "PL"

    league_logo = f"{league_name}.png"

    print(f"League name is {league_name}")

    conn = sqlite3.connect('/Users/jason/PycharmProjects/soccer/templates/football_matches.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT home_team, away_team, match_date 
        FROM matches 
        WHERE league = ?
    ''', (league_name,))
    match_fixtures = cursor.fetchall()
    conn.close()

    # with open(f'stats/fixtures_{league_name}.txt') as file:
    #     match_fixtures = file.read().splitlines()

    # matches = parse_matches(match_fixtures)
    fixtures_text = f"Displaying fixtures for the {league_text}"

    # sorted_form = dict(sorted(form.items(), key=lambda x: calculate_points(x[1]), reverse=True))
    # Sort the dictionary based on the calculated points
    # Process and sort the teams

    return render_template("fixtures.html",
                           league_logo=league_logo, fixtures=match_fixtures, form_text=fixtures_text,
                           current_league=league_name, counter=count,
                           current_month=current_month_text, current_day=current_day,
                           current_year=current_year_full)


@app.route("/teams/<team_name>", methods=["GET", "POST"])
def team_page(team_name):
    team_name = team_name.replace("-", " ")  # Convert URL-friendly name back
    stats = team_stats.get(team_name, None)
    # return render_template("team.html", team=team_name, stats=stats)
    conn = sqlite3.connect('/Users/jason/PycharmProjects/soccer/templates/football_matches.db')
    cursor = conn.cursor()
    cursor.execute('''
         SELECT form  
         FROM form 
         WHERE team = ?
     ''', (team_name,))
    team_form = cursor.fetchall()
    get_team_form = team_form[0][0]

    cursor.execute('''
             SELECT form  
             FROM home_form 
             WHERE team = ?
         ''', (team_name,))
    home_form = cursor.fetchall()
    get_home_form = home_form[0][0]

    cursor.execute('''
             SELECT form  
             FROM away_form 
             WHERE team = ?
         ''', (team_name,))
    home_form = cursor.fetchall()
    get_away_form = home_form[0][0]

    cursor.execute('''
             SELECT home_team,home_score,away_team,away_score  
             FROM detailed_results 
             WHERE home_team = ? or away_team = ?
         ''', (team_name, team_name))
    results = cursor.fetchall()

    cursor.execute('''
             SELECT home_team,home_score,away_team,away_score  
             FROM detailed_results 
             WHERE home_team = ?
         ''', (team_name,))
    home_results = cursor.fetchall()

    cursor.execute('''
             SELECT home_team,home_score,away_team,away_score  
             FROM detailed_results 
             WHERE away_team = ?
         ''', (team_name,))
    away_results = cursor.fetchall()

    conn.close()

    # Extract the string

    # Remove any unwanted characters (only keep W, D, or L)
    team_form_cleaned = re.sub(r'[^WDL]', '', get_team_form)
    home_form_cleaned = re.sub(r'[^WDL]', '', get_home_form)
    away_form_cleaned = re.sub(r'[^WDL]', '', get_away_form)
    return render_template("team.html", team=team_name, team_form=team_form_cleaned, home_form=home_form_cleaned, away_form=away_form_cleaned, results=results,
                           home_results=home_results, away_results=away_results )


@app.route('/championship', methods=["GET", "POST"])
def show_championship():
    league_name = "ELC"
    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

    count = 0
    post_obj = []
    teams = []
    homeForm = {}
    awayForm = {}
    form = {}
    name = ""
    league_logo = "ELC.png"
    with open(f'stats/results_{league_name}.txt') as f:
        results = f.read().splitlines()

    with open(f'stats/teams_{league_name}.txt') as f:
        teams = f.read().splitlines()

    with open(f'stats/team_form_{league_name}.json') as file:
        form = json.load(file)

    teams.sort()

    sorted_form = dict(sorted(form.items(), key=lambda x: calculate_points(x[1]), reverse=True))

    return render_template("main_football_page.html", all_posts=post_obj, all_teams=teams, form=sorted_form,
                           counter=count,
                           selectedTeam=name, current_month=current_month_text, current_day=current_day,
                           current_league=league_name, league_logo=league_logo,
                           current_year=current_year_full)


@app.route('/premier_league', methods=["GET", "POST"])
def show_premiership():
    league_name = "PL"
    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

    count = 0
    post_obj = []
    teams = []
    homeForm = {}
    awayForm = {}
    form = {}
    name = ""
    league_logo = "PL.png"

    with open(f'stats/results_{league_name}.txt') as f:
        results = f.read().splitlines()

    with open(f'stats/teams_{league_name}.txt') as f:
        teams = f.read().splitlines()

    with open(f'stats/team_form_{league_name}.json') as file:
        form = json.load(file)

    sorted_form = dict(sorted(form.items(), key=lambda x: calculate_points(x[1]), reverse=True))

    return render_template("main_football_page.html", all_posts=post_obj, all_teams=teams, form=sorted_form,
                           counter=count,
                           selectedTeam=name, current_month=current_month_text, current_day=current_day,
                           league_logo=league_logo,
                           current_league=league_name,
                           current_year=current_year_full)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    # return send_from_directory('/static/files/', 'cheat_sheet.pdf')
    return send_from_directory('static', path="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
