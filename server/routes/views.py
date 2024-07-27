from flask import Blueprint, render_template, request, flash, redirect, url_for
from routes import dataServices as dataServices
views = Blueprint('views', __name__)

@views.route('/')
def home():
    playerid_df = dataServices.fromSQL('playerid')
    playersId = playerid_df.to_dict(orient='records')
    return render_template('home.html', playersId=playersId)

@views.route('/ai')
def matchups_home():
    return render_template('matchupsHome.html')
