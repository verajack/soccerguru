from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import requests
from datetime import datetime


match=[]

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

    uri = 'https://api.football-data.org/v4/competitions/ELC/matches?status=FINISHED'
    headers = { 'X-Auth-Token': '611a49203eca499a90945814f14d0d8f' }
    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

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
        #print(f"Hometeam is {homeTeam}")
        awayTeam = str(match['awayTeam']['name'])
        #print(f"AwayTeam is {awayTeam}")

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
    print(teams)

    return render_template("main_football_page.html", name=current_user.name, logged_in=True, all_posts=post_obj, all_teams=teams,form=form, counter=count, current_month=current_month_text, current_day=current_day, current_year=current_year_full)

@app.route('/teams', methods=['POST'])
def show_team_scores():

    uri = 'https://api.football-data.org/v4/competitions/ELC/matches?status=FINISHED'
    headers = { 'X-Auth-Token': '611a49203eca499a90945814f14d0d8f' }
    current_month_text = datetime.now().strftime('%B')
    current_day = datetime.now().strftime('%d')
    current_year_full = datetime.now().strftime('%Y')

    count=0
    post_obj=[]
    teams=[]
    homeForm={}
    awayForm={}
    form={}
    name=""
    response = requests.get(uri, headers=headers)
    name = request.form["teamlist"]
    for match in response.json()['matches']:
        count=count+1
        if (match['awayTeam']['name'] == name) or (match['homeTeam']['name'] == name):
            post_obj.append(f"{match['homeTeam']['name']} {match['score']['fullTime']['home']} : {match['score']['fullTime']['away']} {match['awayTeam']['name']}")
        if (match['awayTeam']['name'] not in teams ):
            teams.append(f"{match['awayTeam']['name']}")
    teams.sort()

    return render_template("main_football_page.html", all_posts=post_obj, all_teams=teams,form=form, counter=count, selectedTeam=name, current_month=current_month_text, current_day=current_day, current_year=current_year_full)


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
