import sqlite3
from datetime import datetime
import json
import requests


def create_db():
    conn = sqlite3.connect('/Users/jason/PycharmProjects/soccer/templates/football_matches.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detailed_results (
            id INTEGER PRIMARY KEY,
            league TEXT,
            home_team TEXT,
            home_score INT,
            away_team TEXT,
            away_score INT,
            UNIQUE (league, home_team, away_team)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id,
            league TEXT,
            team TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY,
            league TEXT,
            result TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS form (
            league TEXT,
            team TEXT UNIQUE,
            form TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS home_form (
            league TEXT,
            team TEXT UNIQUE,
            form TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS away_form (
            league TEXT,
            team TEXT UNIQUE,
            form TEXT
        )
    ''')

    # Create a table for matches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY,
            league TEXT,
            home_team TEXT,
            away_team TEXT,
            match_date TEXT
        )
    ''')

    # Create a table for team stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_stats (
            team_name TEXT UNIQUE,
            wins INTEGER,
            losses INTEGER,
            draws INTEGER,
            points INTEGER
        )
    ''')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='matches'")
    table_exists = cursor.fetchone()

    if table_exists:
        print("✅ Table 'matches' exists!")
    else:
        print("❌ Table 'matches' does NOT exist!")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_db()
    print("Database created successfully!")

