from flask import Blueprint, g, render_template, request, redirect, url_for
import requests
import pandas as pd
from routes import apiServices as apiServices
from routes import searchServices as searchServices
from routes import dataServices as dataServices
from sqlalchemy import create_engine, text
from os import environ

search = Blueprint('search', __name__)

#custom filter to allow jinja to use functions
@search.app_template_filter('minutes_seconds')
def minutes_seconds_filter(decimal_minutes):
    minutes, seconds = searchServices.convert_to_minutes_seconds(decimal_minutes)
    return f"{minutes}m {seconds}s"

#Route for displaying player match histories
@search.route('/match/<gameName>/<tagLine>')
def match_stats(gameName, tagLine):
    puuid = ''
    playerid_df = dataServices.fromSQL('playerid')
    matchId_df = dataServices.fromSQL('matchlist')
    matchhistory_df = dataServices.fromSQL('matchhistory')

    nameExists = playerid_df.index[playerid_df['gameName'].str.lower() == gameName.lower()].tolist()
    if nameExists:
        for nameIndex in nameExists:
            if playerid_df['tagLine'][nameIndex].lower() == tagLine.lower():
                puuid = playerid_df['puuid'][nameIndex]
    else:
        puuid = apiServices.get_puuid_FromGameName(gameName, tagLine)
        if puuid == None:
            return redirect(url_for('views.home'))
        profileIconId, summonerLevel, summonerId, gameName, tagLine = apiServices.get_summonerInfo_FromPuuid(puuid)

    matches = apiServices.get_matchlist_FromPuuid(puuid)

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
            dataServices.toSQL(matchlist_df, 'matchlist', 'append')

            match_df = apiServices.processMatchData(apiServices.get_match(match), puuid)
            match_df['uuid'] = f'{puuid}_{match}'
            dataServices.toSQL(match_df, 'matchhistory', 'append')
            match_history.append(match_df.iloc[0])
            
            searchServices.matchStats(match_df, 0, win_history, avg_kda, avg_cs, wr, remakeCounter)
        else:
            matchDataExists = matchhistory_df.index[matchhistory_df['uuid'] == f'{puuid}_{match}'].tolist()
            if matchDataExists:
                match_history.append(matchhistory_df.iloc[matchDataExists[0]])

                searchServices.matchStats(matchhistory_df, matchDataExists[0], win_history, avg_kda, avg_cs, wr, remakeCounter)
            else:
                match_df = apiServices.processMatchData(apiServices.get_match(match), puuid)
                match_df['uuid'] = f'{puuid}_{match}'
                dataServices.toSQL(match_df, 'matchhistory', 'append')
                match_history.append(match_df.iloc[0])

                searchServices.matchStats(match_df, 0, win_history, avg_kda, avg_cs, wr, remakeCounter)

    df = pd.DataFrame(match_history)
    matchHistory = df.to_dict(orient='records')

    return render_template('matches.html', matchHistory=enumerate(matchHistory, start=0), winList=win_history, wr=(wr/(len(match_history)-remakeCounter))*100, avg_kda=avg_kda/(len(match_history)-remakeCounter), avg_cs=avg_cs/(len(match_history)-remakeCounter))

#Route for showing top players of LOL
@search.route('/leaderboard')
def get_leaderboard():
    chal_response = apiServices.get_leaderboard("challenger")
    #gm_response = requests.get(root+gm)
    #master_response = requests.get(root+master)

    chal_df = pd.DataFrame(chal_response['entries']).sort_values('leaguePoints', ascending=False).reset_index(drop=True)
    chal_df.index = chal_df.index + 1
    chal_df = chal_df.head(50)

    summonerGameNames = []
    summonerTagLines = []
    summonerIcons = []
    summonerLevels =[]
    playerid_df = dataServices.fromSQL('playerid')
    
    for id in chal_df['summonerId']:
        index = playerid_df.index[playerid_df['summonerId'] == id].tolist()
        if index:
            puuid = playerid_df['puuid'][index[0]]
            gameName = playerid_df['gameName'][index[0]]
            tagLine = playerid_df['tagLine'][index[0]]
            profileIconId = playerid_df['profileIconId'][index[0]]
            summonerLevel = playerid_df['summonerLevel'][index[0]]
        else:
            profileIconId, summonerLevel, puuid, gameName, tagLine = apiServices.get_summonerInfo_FromSummonerId(id)

        summonerGameNames.append(gameName)
        summonerTagLines.append(tagLine)
        summonerIcons.append(profileIconId)
        summonerLevels.append(summonerLevel)

    leaderboard = searchServices.test(chal_df, summonerGameNames, summonerTagLines, summonerIcons, summonerLevels)

    return render_template('leaderboards.html', leaderboard=enumerate(leaderboard, start=1))

#Redirects from searchbar to search function decorator
@search.route('/search', methods=['get', 'post'])
def search_redirect():
    if request.method == 'POST':
        value = request.form.get('playerSearch')
        parts = value.split('#')
        if len(parts) == 1:
            return redirect(url_for('views.home'))
        gameName = parts[0]
        tagLine = parts[1]
        return redirect(url_for('search.match_stats', gameName=gameName, tagLine=tagLine))
    
    return redirect(url_for('views.home'))