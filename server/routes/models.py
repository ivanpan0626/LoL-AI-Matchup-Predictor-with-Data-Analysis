from flask import Blueprint, render_template, request, flash, redirect, url_for
import json
import pandas as pd
from routes import services as lolapi
from routes import ai as ai
from tensorflow.keras.models import load_model
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os
import pickle

models = Blueprint('models', __name__)

base_dir = os.path.abspath(os.path.dirname(__file__))

championId_path = os.path.join(base_dir, 'data/championId_dict.json')
championTopId_path = os.path.join(base_dir, 'data/championTopId_dict.json')
neuralModel_path = os.path.join(base_dir, 'data/NeuralMatchUpAIModel.keras')
RFModel_path = os.path.join(base_dir, 'data/RandomForestTeamMatchupModel.pkl')

neuralModel = load_model(neuralModel_path)
with open(RFModel_path, 'rb') as file:
    RFmodel = pickle.load(file)

with open(championId_path, 'r') as file:
    championId_dict = json.load(file)
with open(championTopId_path, 'r') as file:
    championTopId_dict = json.load(file)

def matchupCalc(champ1, champ2):
    x, x_features = ai.preprocessMatchup(champ1, champ2)
    pred = neuralModel.predict([x['redTeam_mapped'], x['blueTeam_mapped'], x_features])
    return pred

@models.route('/lane_matchup', methods=['POST', 'GET'])
def lane_matchup():
    if request.method == 'POST':
        champ1 = request.form.get('champ1')
        champ2 = request.form.get('champ2')
        if champ1 not in championId_dict.values():
            return render_template('lanematchup.html', test='Invalid Red Team Champion Name')
        if champ2 not in championId_dict.values():
            return render_template('lanematchup.html', test='Invalid Blue Team Champion Name')
        
        pred = matchupCalc(champ1, champ2)
        pred_reverse = matchupCalc(champ2, champ1)
        pred[0][0] = .50 + (pred[0][0]-pred_reverse[0][0])
        return render_template('lanematchup.html', test=pred[0][0])
        
    return render_template('lanematchup.html')

@models.route('/lane_matchup_rec', methods=['POST', 'GET'])
def lane_matchup_rec():
    if request.method == 'POST':
        champ2 = request.form.get('champ2')
        if champ2 not in championId_dict.values():
            return render_template('lanematchuprec.html', test='Invalid Red Team Champion Name')
        
        highestWR = [0.00, 0.00, 0.00]
        champName = ['test','test','test']
        for champ1 in championTopId_dict.values():
            pred = matchupCalc(champ1, champ2)
            pred_reverse = matchupCalc(champ2, champ1)
            pred[0][0] = .50 + (pred[0][0]-pred_reverse[0][0])
            if pred[0][0] > highestWR[2]:
                if pred[0][0] > highestWR[1]:
                    if pred[0][0] > highestWR[0]:
                        highestWR[0] = pred[0][0]
                        champName[0] = champ1
                    else:
                        highestWR[1] = pred[0][0]
                        champName[1] = champ1
                else:
                    highestWR[2] = pred[0][0]
                    champName[2] = champ1

        return render_template('lanematchuprec.html', test=highestWR, testChamps=champName)
        
    return render_template('lanematchuprec.html')

@models.route('/team_matchup', methods=['POST', 'GET'])
def team_matchup():
    if request.method == 'POST':
        side = 'red'
        for i in range(1,11):
            champ = request.form.get(f'champ{i}')
            if champ not in championId_dict.values():
                return render_template('teammatchup.html', test=f'Invalid Champion name at index {i}')
            if i > 5:
                side = 'blue'
            ai.createChampionData(champ, side)

        x = ai.preprocessTeamMatchup(ai.appendItems())
        pred = RFmodel.predict_proba(x)[:, 1]
        y_pred = RFmodel.predict(x)
        print(y_pred)
        print(pred)
        return render_template('teammatchup.html', test=pred[0])
        
    return render_template('teammatchup.html')