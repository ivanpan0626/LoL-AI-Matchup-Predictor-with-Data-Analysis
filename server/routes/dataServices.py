import pandas as pd
import json
import re
import os
from os import environ
from sqlalchemy import create_engine, text
from routes import apiServices as apiServices

db_engine = create_engine(environ.get('DB_URL'), pool_recycle=3600)

base_dir = os.path.abspath(os.path.dirname(__file__))

championId_path = os.path.join(base_dir, 'data/championId_dict.json')
csv_path = os.path.join(base_dir, 'data/champion_data_df.csv')

champion_data_df = pd.read_csv(csv_path)
champion_data_df = champion_data_df.drop(columns=['Unnamed: 0'])

with open(championId_path, 'r') as file:
    championId_dict = json.load(file)

def merge_champion_stats(all_match_df, champion_data_df):
    all_matchData_df = all_match_df.copy()

    pattern = re.compile(r'^(redTeam|blueTeam)$')
    for index, row in all_match_df.iterrows():
        for col in all_match_df.columns:
            if pattern.match(col):
                champion_name = all_match_df.loc[index, col]
                stats = champion_data_df[champion_data_df['name'] == champion_name]
                if not stats.empty:
                    for stat_col in champion_data_df.columns:
                        if stat_col != 'name' and stat_col != 'matches' :
                            all_matchData_df.loc[index, f"{col}_{stat_col}"] = stats[stat_col].values[0]

    all_matchData_df[f'redTeam_win_rate'] = all_matchData_df[f'redTeam_win_rate'].str.rstrip('%').astype(float)
    all_matchData_df[f'redTeam_pick_rate'] = all_matchData_df[f'redTeam_pick_rate'].str.rstrip('%').astype(float)
    all_matchData_df[f'redTeam_ban_rate'] = all_matchData_df[f'redTeam_ban_rate'].str.rstrip('%').astype(float)
    all_matchData_df[f'redTeam_rank'] = all_matchData_df[f'redTeam_rank'].str.rstrip('%').astype(float)

    all_matchData_df[f'blueTeam_win_rate'] = all_matchData_df[f'blueTeam_win_rate'].str.rstrip('%').astype(float)
    all_matchData_df[f'blueTeam_pick_rate'] = all_matchData_df[f'blueTeam_pick_rate'].str.rstrip('%').astype(float)
    all_matchData_df[f'blueTeam_ban_rate'] = all_matchData_df[f'blueTeam_ban_rate'].str.rstrip('%').astype(float)
    all_matchData_df[f'blueTeam_rank'] = all_matchData_df[f'blueTeam_rank'].str.rstrip('%').astype(float)

    return all_matchData_df

def processMatchData(matchData, puuid):
    metadata = matchData['metadata']
    info = matchData['info']
    players = info['participants']
    match_id = metadata['matchId']
    participants = metadata['participants']
    teams = info['teams']
    player = players[participants.index(puuid)]

    #rune organization
    perks = player['perks']
    styles = perks['styles']

    primary = styles[0]
    secondary = styles[1]

    gameNames = []
    tagLines = []
    with db_engine.connect() as connection:
        playerid_df = pd.read_sql(text('SELECT * FROM "summonerdata".playerid;'), connection)

    for i in range(0,10):
        puuidExists = playerid_df.index[playerid_df['puuid'] == participants[i]].tolist()
        if puuidExists:
            gameNames.append(playerid_df.iloc[puuidExists[0]]['gameName'])
            tagLines.append(playerid_df.iloc[puuidExists[0]]['tagLine'])
        else:
            profileIconId, summonerLevel, summonerId, gameName, tagLine = apiServices.get_summonerInfo_FromPuuid(participants[i])
            new_row = {'puuid' : participants[i], 
                    'summonerId' : summonerId, 
                    'gameName': gameName, 
                    'tagLine': tagLine, 
                    'profileIconId': profileIconId, 
                    'summonerLevel' : summonerLevel}
            
            df = pd.DataFrame([new_row])
            df.to_sql('playerid', con=db_engine, schema='summonerdata', if_exists='append', index=False)

            gameNames.append(gameName)
            tagLines.append(tagLine)

    playerData_df = pd.DataFrame([{
        #game info
        'game_duration' : info['gameDuration']/60,
        'patch' : info['gameVersion'],

        #all champions
        'p1ChampId' : players[0]['championId'],
        'p1GameName' : gameNames[0],
        'p1TagLine' : tagLines[0],
        

        'p2ChampId' : players[1]['championId'],
        'p2GameName' : gameNames[1],
        'p2TagLine' : tagLines[1],

        'p3ChampId' : players[2]['championId'],
        'p3GameName' : gameNames[2],
        'p3TagLine' : tagLines[2],

        'p4ChampId' : players[3]['championId'],
        'p4GameName' : gameNames[3],
        'p4TagLine' : tagLines[3],

        'p5ChampId' : players[4]['championId'],
        'p5GameName' : gameNames[4],
        'p5TagLine' : tagLines[4],

        'p6ChampId' : players[5]['championId'],
        'p6GameName' : gameNames[5],
        'p6TagLine' : tagLines[5],

        'p7ChampId' : players[6]['championId'],
        'p7GameName' : gameNames[6],
        'p7TagLine' : tagLines[6],

        'p8ChampId' : players[7]['championId'],
        'p8GameName' : gameNames[7],
        'p8TagLine' : tagLines[7],

        'p9ChampId' : players[8]['championId'],
        'p9GameName' : gameNames[8],
        'p9TagLine' : tagLines[8],

        'p10ChampId' : players[9]['championId'],
        'p10GameName' : gameNames[9],
        'p10TagLine' : tagLines[9],

        #player team
        'win' : player['win'],
        'teamId' : player['teamId'],
        'position' : player['teamPosition'],

        #runes
        'primary_keystone' : primary['selections'][0]['perk'],
        'primary_perk_1' : primary['selections'][1]['perk'],
        'primary_perk_2' : primary['selections'][2]['perk'],
        'primary_perk_3' : primary['selections'][3]['perk'],

        'secondary_keystone' : secondary['selections'][0]['perk'],
        'secondary_perk_1' : secondary['selections'][1]['perk'],
        #'secondary_perk_2' : secondary['selections'][2]['perk'],


        #player kda
        'kills' : player['kills'],
        'deaths' : player['deaths'],
        'assists' : player['assists'],

        #player stats
        'visionScore' : player['visionScore'],
        'wardsKilled' : player['wardsKilled'],
        'wardsPlaced' : player['wardsPlaced'],
        'visionWardsBoughtInGame' : player['visionWardsBoughtInGame'],

        'totalCreepScore': player['totalMinionsKilled']+player['neutralMinionsKilled'],

        'firstBloodKill' : player['firstBloodKill'],
        'firstBloodAssist' : player['firstBloodAssist'],
        'firstTowerKill' : player['firstTowerKill'],
        'firstTowerAssist' : player['firstTowerAssist'],

        'turretTakedowns' : player['turretTakedowns'],

        'goldEarned' : player['goldEarned'],

        #player items
        'item0' : player['item0'],
        'item1' : player['item1'],
        'item2' : player['item2'],
        'item3' : player['item3'],
        'item4' : player['item4'],
        'item5' : player['item5'],
        'item6' : player['item6'],

        #advanced damage dealt/taken stats
        'inhibitorTakedowns' : player['inhibitorTakedowns'],
        'damageDealtToObjectives': player['damageDealtToObjectives'],
        'damageDealtToTurrets' : player['damageDealtToTurrets'],
        'damageSelfMitigated' : player['damageSelfMitigated'],

        'physicalDamageDealtToChampions' : player['physicalDamageDealtToChampions'],
        'physicalDamageDealt' : player['physicalDamageDealt'],
        'physicalDamageTaken' : player['physicalDamageTaken'],

        'magicDamageDealtToChampions' : player['magicDamageDealtToChampions'],
        'magicDamageDealt' : player['magicDamageDealt'],
        'magicDamageTaken' : player['magicDamageTaken'],

        'totalDamageDealtToChampions' : player['totalDamageDealtToChampions'],
        'totalDamageDealt' : player['totalDamageDealt'],
        'totalDamageTaken' : player['totalDamageTaken'],

        'totalHeal' : player['totalHeal'],
        'totalHealsOnTeammates' : player['totalHealsOnTeammates'],
        'totalDamageShieldedOnTeammates' : player['totalDamageShieldedOnTeammates'],

        #killing sprees
        'doubleKills' : player['doubleKills'],
        'tripleKills' : player['tripleKills'],
        'quadraKills' : player['quadraKills'],
        'pentaKills' : player['pentaKills'],
        'killingSprees' : player['killingSprees'],


        #champion info
        'champLevel' : player['champLevel'],
        'championId' : player['championId'],
        'championName' : player['championName'],
        'championTransform' : player['championTransform'],
    }])

    return playerData_df

def processMatchDataV2(match):
    redTeamChamps = []
    redTeamRoles = []
    redTeamWRs = []
    redTeamPickRates = []
    redTeamBanRates = []
    redTeamTiers = []
    redTeamRanks = []

    blueTeamChamps = []
    blueTeamRoles = []
    blueTeamWRs = []
    blueTeamPickRates = []
    blueTeamBanRates = []
    blueTeamTiers = []
    blueTeamRanks = []

    outcome = 0
    participants = match['metadata']['participants']
    players = match['info']['participants']

    if match['info']['participants'][0]['win'] == False:
        if match['info']['participants'][0]['teamId'] == 200:
            outcome = 0
        else:
            outcome = 1
    else:
        if match['info']['participants'][0]['teamId'] == 200:
            outcome = 1
        else:
            outcome = 0
    #0 indicates blue side win, 1 indicates red side win

    def get_index(puuid):
        index = players[participants.index(puuid)]
        return index
    
    def get_championData(name):
        temp_df = champion_data_df[champion_data_df['name'].str.contains(name, case=False)]
        wr = temp_df['win_rate'].str.rstrip('%').astype(float).iloc[0]
        pr = temp_df['pick_rate'].str.rstrip('%').astype(float).iloc[0]
        br = temp_df['ban_rate'].str.rstrip('%').astype(float).iloc[0]
        tier = temp_df['tier'].iloc[0]
        rank = temp_df['rank'].str.rstrip('%').astype(float).iloc[0]

        return wr, pr, br, tier, rank
    
    for player in participants:
        player = get_index(player)
        if player['teamId'] == 200:
            wr, pr, br, tier, rank = get_championData(championId_dict[str(player['championId'])])
            redTeamChamps.append(championId_dict[str(player['championId'])])
            redTeamRoles.append(player['teamPosition'])
            redTeamWRs.append(wr)
            redTeamPickRates.append(pr)
            redTeamBanRates.append(br)
            redTeamTiers.append(tier)
            redTeamRanks.append(rank)
        else:
            wr, pr, br, tier, rank = get_championData(championId_dict[str(player['championId'])])
            blueTeamChamps.append(championId_dict[str(player['championId'])])
            blueTeamRoles.append(player['teamPosition'])
            blueTeamWRs.append(wr)
            blueTeamPickRates.append(pr)
            blueTeamBanRates.append(br)
            blueTeamTiers.append(tier)
            blueTeamRanks.append(rank)
    
    match_info = pd.DataFrame([{
        'outcome' : outcome,

        #red team
        'redTeam' : redTeamChamps,
        'redTeamRoles' : redTeamRoles,
        'redTeamWinRates' : redTeamWRs,
        'redTeamPickRatesm' : redTeamPickRates,
        'redTeamBanRates' : redTeamBanRates,
        'redTeamTiers' : redTeamTiers,
        'redTeamRanks' : redTeamRanks,
        #blue team
        'blueTeam' : blueTeamChamps,
        'blueTeamRoles' : blueTeamRoles,
        'blueTeamWinRates' : blueTeamWRs,
        'blueTeamPickRatesm' : blueTeamPickRates,
        'blueTeamBanRates' : blueTeamBanRates,
        'blueTeamTiers' : blueTeamTiers,
        'blueTeamRanks' : blueTeamRanks,
    }])
    return match_info

def processMatchDataV3(match): #Cleans up individual Match data for dataframe that feeds to AI
    redTeamChamps = []
    redTeamRoles = []
    blueTeamChamps = []
    blueTeamRoles = []
    outcome = 0
    participants = match['metadata']['participants']
    players = match['info']['participants']

    # 1 indicates Red win, 0 indicates Blue win
    if match['info']['participants'][0]['win'] == False:
        if match['info']['participants'][0]['teamId'] == 200:
            outcome = 0
        else:
            outcome = 1
    else:
        if match['info']['participants'][0]['teamId'] == 200:
            outcome = 1
        else:
            outcome = 0

    def get_index(puuid):
        index = players[participants.index(puuid)]
        return index
    
    for player in participants:
        player = get_index(player)
        if player['teamId'] == 200:
            redTeamChamps.append(player['championId'])
            redTeamRoles.append(player['teamPosition'])
        else:
            blueTeamChamps.append(player['championId'])
            blueTeamRoles.append(player['teamPosition'])
    
    matchInfo = pd.DataFrame()

    for i in range(0,5):
        match = pd.DataFrame([{
            'outcome' : outcome,

            'redTeam' : redTeamChamps[i],
            'blueTeam' : blueTeamChamps[i],

            'Role' : redTeamRoles[i]
        }])
        matchInfo = pd.concat([matchInfo, match])

    return matchInfo

def dataCollect(matchData, puuid):
    dfv2 = processMatchDataV2(matchData)
    dfv2.to_sql('matchv2datatemp', con=db_engine, schema='summonerdata', if_exists='append', index=False)
    dfv3 = processMatchDataV3(matchData)
    dfv3.to_sql('matchv3datatemp', con=db_engine, schema='summonerdata', if_exists='append', index=False)
    return processMatchData(matchData, puuid)