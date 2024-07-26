from flask import Blueprint, render_template, request, flash, redirect, url_for

from routes import services as lolapi

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('base.html')

@views.route('/ai')
def matchups_home():
    return render_template('matchups.html')
