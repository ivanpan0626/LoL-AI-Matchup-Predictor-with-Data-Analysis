import pandas as pd
from routes import apiServices as apiServices
from routes import matchdata as matchProcess
from sqlalchemy import create_engine, text
from os import environ

db_engine = create_engine(environ.get('DB_URL'), pool_recycle=3600)

def toSQL(data, tableName, type):
    data.to_sql(tableName, con=db_engine, schema='summonerdata', if_exists=type, index=False)

def fromSQL(tableName):
    return pd.read_sql(text(f'SELECT * FROM "summonerdata".{tableName};'), db_engine.connect())

def merge_champion_stats(all_match_df, champion_data_df):
    return matchProcess.merge_champion_stats(all_match_df, champion_data_df)

def matchDataCollect(matchData, puuid):
    #storeMatchData(matchData)
    return matchProcess.processMatchData(matchData, puuid)

def storeMatchData(matchData):
    dfv2 = matchProcess.processMatchDataV2(matchData)
    toSQL(dfv2, 'matchv2datatemp', 'append')
    dfv3 = matchProcess.processMatchDataV3(matchData)
    toSQL(dfv3, 'matchv3datatemp', 'append')

def savePlayerId(puuid, summonerId, gameName, tagLine, profileIconId, summonerLevel):
    new_row = {'puuid' : puuid, 
                'summonerId' : summonerId, 
                'gameName': gameName, 
                'tagLine': tagLine, 
                'profileIconId': profileIconId, 
                'summonerLevel' : summonerLevel
                }
            
    df = pd.DataFrame([new_row])
    toSQL(df, 'playerid', 'append')