from flask import Blueprint, render_template, request, flash, redirect, url_for
import requests
import pandas as pd
from routes import apiServices as lolapi
from sqlalchemy import create_engine, text
from os import environ

search = Blueprint('search', __name__)

#Converts gameDuration to minute/seconds
def convert_to_minutes_seconds(decimal_minutes):
    minutes = int(decimal_minutes)
    seconds = (decimal_minutes - minutes) * 60
    return minutes, int(seconds)

#custom filter to allow jinja to use functions
@search.app_template_filter('minutes_seconds')
def minutes_seconds_filter(decimal_minutes):
    minutes, seconds = convert_to_minutes_seconds(decimal_minutes)
    return f"{minutes}m {seconds}s"

#Route for displaying player match histories
@search.route('/match/<gameName>/<tagLine>')
def match_stats(gameName, tagLine):
    puuid = ''
    db_engine = create_engine(environ.get('DB_URL'), pool_recycle=3600)
    with db_engine.connect() as connection:
        playerid_df = pd.read_sql(text('SELECT * FROM "summonerdata".playerid;'), connection)
        matchId_df = pd.read_sql(text('SELECT * FROM "summonerdata".matchlist;'), connection)
        matchhistory_df = pd.read_sql(text('SELECT * FROM "summonerdata".matchhistory;'), connection)

    nameExists = playerid_df.index[playerid_df['gameName'].str.lower() == gameName.lower()].tolist()
    if nameExists:
        for nameIndex in nameExists:
            if playerid_df['tagLine'][nameIndex].lower() == tagLine.lower():
                puuid = playerid_df['puuid'][nameIndex]
    else:
        puuid = lolapi.get_puuid_FromGameName(gameName, tagLine)
        profileIconId, summonerLevel, summonerId, gameName, tagLine = lolapi.get_summonerInfo_FromPuuid(puuid)
        new_row = {'puuid' : puuid, 
                    'summonerId' : summonerId, 
                    'gameName': gameName, 
                    'tagLine': tagLine, 
                    'profileIconId': profileIconId, 
                    'summonerLevel' : summonerLevel}
            
        df = pd.DataFrame([new_row])
        df.to_sql('playerid', con=db_engine, schema='summonerdata', if_exists='append', index=False)

    matches = lolapi.get_matchlist_FromPuuid(puuid)
    
    match_history = []
    win_history = []
    avg_kda = 0
    avg_cs = 0
    wr = 0
    remakeCounter = 0
    for match in matches:
        matchExists = matchId_df.index[matchId_df['matchId'] == match].tolist()
        if not matchExists:
            new_row = {'matchId' : match}
            matchlist_df = pd.DataFrame([new_row])
            matchlist_df.to_sql('matchlist', con=db_engine, schema='summonerdata', if_exists='append', index=False)

            match_df = lolapi.processMatchData(lolapi.get_match(match), puuid)
            match_df['uuid'] = f'{puuid}_{match}'
            match_df.to_sql('matchhistory', con=db_engine, schema='summonerdata', if_exists='append', index=False)
            match_history.append(match_df.iloc[0])
            avg_cs += match_df.iloc[0]['totalCreepScore']
        
            if match_df.iloc[0]['win'] == True:
                if match_df.iloc[0]['deaths'] == 0:
                    avg_kda += (match_df.iloc[0]['kills']+match_df.iloc[0]['assists'])/1
                else:
                    avg_kda += (match_df.iloc[0]['kills']+match_df.iloc[0]['assists'])/match_df.iloc[0]['deaths']
                win_history.append('Win')
                wr += 1
            else:
                if match_df.iloc[0]['totalCreepScore'] == 0:
                    win_history.append('Remake')
                    remakeCounter +=1
                else:
                    if match_df.iloc[0]['deaths'] == 0:
                        avg_kda += (match_df.iloc[0]['kills']+match_df.iloc[0]['assists'])/1
                    else:
                        avg_kda += (match_df.iloc[0]['kills']+match_df.iloc[0]['assists'])/match_df.iloc[0]['deaths']
                    win_history.append('Lose')
        else:
            matchDataExists = matchhistory_df.index[matchhistory_df['uuid'] == f'{puuid}_{match}'].tolist()
            if matchDataExists:
                match_history.append(matchhistory_df.iloc[matchDataExists[0]])
                avg_cs += matchhistory_df.iloc[matchDataExists[0]]['totalCreepScore']
               
                if matchhistory_df.iloc[matchDataExists[0]]['win'] == True:
                    if matchhistory_df.iloc[matchDataExists[0]]['deaths'] == 0:
                        avg_kda += (matchhistory_df.iloc[matchDataExists[0]]['kills']+matchhistory_df.iloc[matchDataExists[0]]['assists'])/1
                    else:
                        avg_kda += (matchhistory_df.iloc[matchDataExists[0]]['kills']+matchhistory_df.iloc[matchDataExists[0]]['assists'])/matchhistory_df.iloc[matchDataExists[0]]['deaths']
                    win_history.append('Win')
                    wr += 1
                else:
                    if matchhistory_df.iloc[matchDataExists[0]]['totalCreepScore'] == 0:
                        win_history.append('Remake')
                        remakeCounter +=1
                    else:
                        if matchhistory_df.iloc[matchDataExists[0]]['deaths'] == 0:
                            avg_kda += (matchhistory_df.iloc[matchDataExists[0]]['kills']+matchhistory_df.iloc[matchDataExists[0]]['assists'])/1
                        else:
                            avg_kda += (matchhistory_df.iloc[matchDataExists[0]]['kills']+matchhistory_df.iloc[matchDataExists[0]]['assists'])/matchhistory_df.iloc[matchDataExists[0]]['deaths']
                        win_history.append('Lose')
            else:
                match_df = lolapi.processMatchData(lolapi.get_match(match), puuid)
                match_df['uuid'] = f'{puuid}_{match}'
                match_df.to_sql('matchhistory', con=db_engine, schema='summonerdata', if_exists='append', index=False)
                match_history.append(match_df.iloc[0])
                avg_cs += match_df.iloc[0]['totalCreepScore']
            
                if match_df.iloc[0]['win'] == True:
                    if match_df.iloc[0]['deaths'] == 0:
                        avg_kda += (match_df.iloc[0]['kills']+match_df.iloc[0]['assists'])/1
                    else:
                        avg_kda += (match_df.iloc[0]['kills']+match_df.iloc[0]['assists'])/match_df.iloc[0]['deaths']
                    win_history.append('Win')
                    wr += 1
                else:
                    if match_df.iloc[0]['totalCreepScore'] == 0:
                        win_history.append('Remake')
                        remakeCounter +=1
                    else:
                        if match_df.iloc[0]['deaths'] == 0:
                            avg_kda += (match_df.iloc[0]['kills']+match_df.iloc[0]['assists'])/1
                        else:
                            avg_kda += (match_df.iloc[0]['kills']+match_df.iloc[0]['assists'])/match_df.iloc[0]['deaths']
                        win_history.append('Lose')

    df = pd.DataFrame(match_history)
    matchHistory = df.to_dict(orient='records')

    #return render_template('matches.html')
    return render_template('matches.html', matchHistory=enumerate(matchHistory, start=0), winList=win_history, wr=(wr/(len(match_history)-remakeCounter))*100, avg_kda=avg_kda/(len(match_history)-remakeCounter), avg_cs=avg_cs/(len(match_history)-remakeCounter))

#Route for showing top players of LOL
@search.route('/leaderboard')
def get_leaderboard():
    chal_response = lolapi.get_leaderboard("challenger")
    #gm_response = requests.get(root+gm)
    #master_response = requests.get(root+master)

    chal_df = pd.DataFrame(chal_response['entries']).sort_values('leaguePoints', ascending=False).reset_index(drop=True)
    chal_df.index = chal_df.index + 1
    chal_df = chal_df.head(50)

    #summonerNames = []
    summonerGameNames = []
    summonerTagLines = []
    summonerIcons = []
    summonerLevels =[]
    db_engine = create_engine(environ.get('DB_URL'), pool_recycle=3600)
    with db_engine.connect() as connection:
        playerid_df = pd.read_sql(text('SELECT * FROM "summonerdata".playerid;'), connection)
    
    for id in chal_df['summonerId']:
        index = playerid_df.index[playerid_df['summonerId'] == id].tolist()
        if index:
            puuid = playerid_df['puuid'][index[0]]
            gameName = playerid_df['gameName'][index[0]]
            tagLine = playerid_df['tagLine'][index[0]]
            profileIconId = playerid_df['profileIconId'][index[0]]
            summonerLevel = playerid_df['summonerLevel'][index[0]]
        else:
            profileIconId, summonerLevel, puuid, gameName, tagLine = lolapi.get_summonerInfo_FromSummonerId(id)

            new_row = {'puuid' : puuid, 
                       'summonerId' : id, 
                       'gameName': gameName, 
                       'tagLine': tagLine, 
                       'profileIconId': profileIconId, 
                       'summonerLevel' : summonerLevel}
            
            df = pd.DataFrame([new_row])
            df.to_sql('playerid', con=db_engine, schema='summonerdata', if_exists='append', index=False)

        #summonerNames.append(f"{gameName}#{tagLine}")
        summonerGameNames.append(gameName)
        summonerTagLines.append(tagLine)
        summonerIcons.append(profileIconId)
        summonerLevels.append(summonerLevel)

    chal_df_new = chal_df[['leaguePoints', 'hotStreak']]
    chal_df_new.insert(0, 'summonerGameName', summonerGameNames)
    chal_df_new.insert(1, 'summonerTagLine', summonerTagLines)
    chal_df_new.insert(2, 'win_rate', (chal_df['wins']/(chal_df['wins']+chal_df['losses'])).apply('{:.0%}'.format))
    chal_df_new.insert(3, 'winloss', chal_df['wins'].astype(str) + '/' + chal_df['losses'].astype(str))
    chal_df_new.insert(4, 'profileIconId', summonerIcons)
    chal_df_new.insert(5, 'summonerLevel', summonerLevels)
    leaderboard = chal_df_new.to_dict(orient='records')

    return render_template('leaderboards.html', leaderboard=enumerate(leaderboard, start=1))

#Redirects from searchbar to search function decorator
@search.route('/search', methods=['post'])
def search_redirect():
    if request.method == 'POST':
        value = request.form.get('value')
        parts = value.split('#')
        gameName = parts[0]
        tagLine = parts[1]
        return redirect(url_for('search.match_stats', gameName=gameName, tagLine=tagLine))
    
    return "hi"