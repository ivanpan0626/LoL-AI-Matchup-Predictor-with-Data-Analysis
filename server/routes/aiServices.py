import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os
import json
import pandas as pd
from routes import apiServices as apiServices
from routes import dataServices as dataServices
import ast

base_dir = os.path.abspath(os.path.dirname(__file__))

championId_path = os.path.join(base_dir, 'data/championId_dict.json')
csv_path = os.path.join(base_dir, 'data/champion_data_df.csv')

champion_data_df = pd.read_csv(csv_path)
champion_data_df = champion_data_df.drop(columns=['Unnamed: 0'])

with open(championId_path, 'r') as file:
    championId_dict = json.load(file)

def preprocessMatchup(champ1, champ2):
    guess_df = pd.DataFrame(columns=['redTeam', 'blueTeam'])

    guess_df.loc[0, 'redTeam'] = champ1
    guess_df.loc[0, 'blueTeam'] = champ2
        
    guess_df = dataServices.merge_champion_stats(guess_df, champion_data_df)

    tiers = ['S+Tier', 'STier', 'ATier', 'BTier', 'CTier', 'DTier']
    tier_label_encoder = LabelEncoder()
    tier_label_encoder.fit(tiers)

    all_champions = []
    for champ in championId_dict.values():
        all_champions.append(champ)
    champ_label_encoder = LabelEncoder()
    champ_label_encoder.fit(all_champions)

    all_champions = champ_label_encoder.transform(all_champions)

    # Fit and transform the data
    guess_df['redTeam'] = champ_label_encoder.transform(guess_df['redTeam'])
    guess_df['redTeam_tier'] = tier_label_encoder.transform(guess_df['redTeam_tier'])

    guess_df['blueTeam'] = champ_label_encoder.transform(guess_df['blueTeam'])
    guess_df['blueTeam_tier'] = tier_label_encoder.transform(guess_df['blueTeam_tier'])

    x = guess_df

    unique_champions = np.unique(all_champions)
    champion_mapping = {champ: i for i, champ in enumerate(unique_champions)}

    x['redTeam_mapped'] = x['redTeam'].map(champion_mapping)
    x['blueTeam_mapped'] = x['blueTeam'].map(champion_mapping)

    x_features = x.drop(columns=['redTeam', 'blueTeam', 'redTeam_mapped', 'blueTeam_mapped']).values

    return x, x_features

##MATCHUP AI ABOVE, TEAM MATCHUP AI BELOW
redTeamChamps = []
#redTeamRoles = []
redTeamWRs = []
redTeamPickRates = []
redTeamBanRates = []
redTeamTiers = []
redTeamRanks = []

blueTeamChamps = []
#blueTeamRoles = []
blueTeamWRs = []
blueTeamPickRates = []
blueTeamBanRates = []
blueTeamTiers = []
blueTeamRanks = []

def get_champion_id(name):
    for champ_id, champ_name in championId_dict.items():
        if champ_name == name:
            return champ_id
    return None

def get_championData(name):
    temp_df = champion_data_df[champion_data_df['name'].str.contains(name, case=False)]
    wr = temp_df['win_rate'].str.rstrip('%').astype(float).iloc[0]
    pr = temp_df['pick_rate'].str.rstrip('%').astype(float).iloc[0]
    br = temp_df['ban_rate'].str.rstrip('%').astype(float).iloc[0]
    tier = temp_df['tier'].iloc[0]
    rank = temp_df['rank'].str.rstrip('%').astype(float).iloc[0]

    return wr, pr, br, tier, rank

def createChampionData(champ, side):
    if side == 'red':
        if get_champion_id(champ) in championId_dict:
            wr, pr, br, tier, rank = get_championData(championId_dict[get_champion_id(champ)])
            redTeamChamps.append(championId_dict[get_champion_id(champ)])
            redTeamWRs.append(wr)
            redTeamPickRates.append(pr)
            redTeamBanRates.append(br)
            redTeamTiers.append(tier)
            redTeamRanks.append(rank)
    else:
        if get_champion_id(champ) in championId_dict:
            wr, pr, br, tier, rank = get_championData(championId_dict[get_champion_id(champ)])
            blueTeamChamps.append(championId_dict[get_champion_id(champ)])
            blueTeamWRs.append(wr)
            blueTeamPickRates.append(pr)
            blueTeamBanRates.append(br)
            blueTeamTiers.append(tier)
            blueTeamRanks.append(rank)

def appendItems():
    match_info = pd.DataFrame([{
        #red team
        'redTeam' : redTeamChamps,
        'redTeamWinRates' : redTeamWRs,
        'redTeamPickRatesm' : redTeamPickRates,
        'redTeamBanRates' : redTeamBanRates,
        'redTeamTiers' : redTeamTiers,
        'redTeamRanks' : redTeamRanks,

        #blue team
        'blueTeam' : blueTeamChamps,
        'blueTeamWinRates' : blueTeamWRs,
        'blueTeamPickRatesm' : blueTeamPickRates,
        'blueTeamBanRates' : blueTeamBanRates,
        'blueTeamTiers' : blueTeamTiers,
        'blueTeamRanks' : blueTeamRanks,
    }])
    return match_info

def preprocessTeamMatchup (match_df):
    tiers = ['S+Tier', 'STier', 'ATier', 'BTier', 'CTier', 'DTier']

    tier_label_encoder = LabelEncoder()

    all_champions = []
    for champ in championId_dict.values():
        all_champions.append(champ)

    champ_label_encoder = LabelEncoder()

    champ_label_encoder.fit(all_champions)
    tier_label_encoder.fit(tiers)

    match_df['redTeam'] = match_df['redTeam'].apply(lambda team: [champ.strip("'") for champ in team])
    match_df['redTeamTiers'] = match_df['redTeamTiers'].apply(lambda team: [champ.strip("'") for champ in team])

    match_df['blueTeam'] = match_df['blueTeam'].apply(lambda team: [champ.strip("'") for champ in team])
    match_df['blueTeamTiers'] = match_df['blueTeamTiers'].apply(lambda team: [champ.strip("'") for champ in team])

    match_df['redTeamWinRates'] = match_df['redTeamWinRates'].apply(lambda x: [float(i) for i in x])
    match_df['blueTeamWinRates'] = match_df['blueTeamWinRates'].apply(lambda x: [float(i) for i in x])
    match_df['redTeamPickRatesm'] = match_df['redTeamPickRatesm'].apply(lambda x: [float(i) for i in x])
    match_df['blueTeamPickRatesm'] = match_df['blueTeamPickRatesm'].apply(lambda x: [float(i) for i in x])
    match_df['redTeamBanRates'] = match_df['redTeamBanRates'].apply(lambda x: [float(i) for i in x])
    match_df['blueTeamBanRates'] = match_df['blueTeamBanRates'].apply(lambda x: [float(i) for i in x])
    match_df['redTeamRanks'] = match_df['redTeamRanks'].apply(lambda x: [float(i) for i in x])
    match_df['blueTeamRanks'] = match_df['blueTeamRanks'].apply(lambda x: [float(i) for i in x])

    match_df['redTeam'] = match_df['redTeam'].apply(lambda x: champ_label_encoder.transform(x))
    match_df['blueTeam'] = match_df['blueTeam'].apply(lambda x: champ_label_encoder.transform(x))
    match_df['redTeamTiers'] = match_df['redTeamTiers'].apply(lambda x: tier_label_encoder.transform(x))
    match_df['blueTeamTiers'] = match_df['blueTeamTiers'].apply(lambda x: tier_label_encoder.transform(x))

    scaler = StandardScaler()

    numerical_features = ['redTeamWinRates', 'blueTeamWinRates', 'redTeamPickRatesm', 'blueTeamPickRatesm', 'redTeamBanRates', 'blueTeamBanRates', 'redTeamRanks', 'blueTeamRanks']

    for feature in numerical_features:
        match_df[feature] = match_df[feature].apply(lambda x: scaler.fit_transform(np.array(x).reshape(-1, 1)).flatten())

    X = np.hstack([
        np.stack(match_df['redTeam'].values),
        np.stack(match_df['blueTeam'].values),
        np.stack(match_df['redTeamWinRates'].values),
        np.stack(match_df['blueTeamWinRates'].values),
        np.stack(match_df['redTeamPickRatesm'].values),
        np.stack(match_df['blueTeamPickRatesm'].values),
        np.stack(match_df['redTeamBanRates'].values),
        np.stack(match_df['blueTeamBanRates'].values),
        np.stack(match_df['redTeamTiers'].values),
        np.stack(match_df['blueTeamTiers'].values),
        np.stack(match_df['redTeamRanks'].values),
        np.stack(match_df['blueTeamRanks'].values)
    ])

    redTeamChamps[:] = []
    redTeamWRs[:] = []
    redTeamPickRates[:] = []
    redTeamBanRates[:] = []
    redTeamTiers[:] = []
    redTeamRanks[:] = []

    blueTeamChamps[:] = []
    blueTeamWRs[:] = []
    blueTeamPickRates[:] = []
    blueTeamBanRates[:] = []
    blueTeamTiers[:] = []
    blueTeamRanks[:] = []

    return X


