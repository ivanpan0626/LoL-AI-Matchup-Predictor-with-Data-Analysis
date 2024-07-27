from flask import Blueprint, render_template, request, flash, redirect, url_for

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')

@views.route('/ai')
def matchups_home():
    return render_template('matchupsHome.html')
