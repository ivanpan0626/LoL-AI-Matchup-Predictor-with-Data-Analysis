from routes import dataCollection as data
import requests
from os import environ


api_key = environ.get('API_KEY')

def get_puuid_FromGameName(gameName, tag):
    url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tag}?api_key={api_key}"
    puuid = requests.get(url).json()['puuid']
    return puuid

def get_riotId_fromPuuid(puuid):
    url = f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={api_key}'
    response = requests.get(url)
    gameName = response.json()['gameName']
    tagLine = response.json()['tagLine']
    return gameName, tagLine

def get_summonerInfo_FromPuuid(puuid):
    url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}'
    response = requests.get(url)
    profileIconId = response.json()['profileIconId']
    summonerLevel = response.json()['summonerLevel']
    summonerId = response.json()['id']

    gameName, tagLine = get_riotId_fromPuuid(puuid)

    return profileIconId, summonerLevel, summonerId, gameName, tagLine

def get_summonerInfo_FromSummonerId(summonerId):
    url = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}?api_key={api_key}'
    response = requests.get(url)
    profileIconId = response.json()['profileIconId']
    summonerLevel = response.json()['summonerLevel']
    puuid = response.json()['puuid']

    gameName, tagLine = get_riotId_fromPuuid(puuid)
    
    return profileIconId, summonerLevel, puuid, gameName, tagLine

def get_matchlist_FromPuuid(puuid):
    #https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start=0&count=20&api_key={api_key}
    #url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key={api_key}"
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start=0&count=5&api_key={api_key}"
    return requests.get(url).json()

def get_match(matchId):
    url = f"https://americas.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={api_key}"
    return requests.get(url).json()

def get_leaderboard(league='challenger'):
    url = f"https://na1.api.riotgames.com/lol/league/v4/{league}leagues/by-queue/RANKED_SOLO_5x5?api_key={api_key}"
    return requests.get(url).json()

def processMatchData(matchData, puuid):
    return data.dataCollect(matchData, puuid)
