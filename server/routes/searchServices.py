#Converts gameDuration to minute/seconds
def convert_to_minutes_seconds(decimal_minutes):
    minutes = int(decimal_minutes)
    seconds = (decimal_minutes - minutes) * 60
    return minutes, int(seconds)

def organizeLeaderboard(chal_df, summonerGameNames, summonerTagLines, summonerIcons, summonerLevels):
    chal_df_new = chal_df[['leaguePoints', 'hotStreak']]
    chal_df_new.insert(0, 'summonerGameName', summonerGameNames)
    chal_df_new.insert(1, 'summonerTagLine', summonerTagLines)
    chal_df_new.insert(2, 'win_rate', (chal_df['wins']/(chal_df['wins']+chal_df['losses'])).apply('{:.0%}'.format))
    chal_df_new.insert(3, 'winloss', chal_df['wins'].astype(str) + 'W/' + chal_df['losses'].astype(str) +'L')
    chal_df_new.insert(4, 'profileIconId', summonerIcons)
    chal_df_new.insert(5, 'summonerLevel', summonerLevels)
    leaderboard = chal_df_new.to_dict(orient='records')

    return leaderboard

def matchStats(match_df, index, win_history, avg_kda, avg_cs, wr, remakeCounter):
    winloss = ''
    kda = 0
    cs = 0
    wr1 = 0
    remakeCounter1 = 0

    cs += match_df.iloc[index]['totalCreepScore']
    if match_df.iloc[index]['win'] == True:
        if match_df.iloc[index]['deaths'] == 0:
            kda += (match_df.iloc[index]['kills']+match_df.iloc[index]['assists'])/1
            winloss = 'Win'
            wr1 += 1
        else:
            kda += (match_df.iloc[index]['kills']+match_df.iloc[index]['assists'])/match_df.iloc[index]['deaths']
            winloss = 'Win'
            wr1 += 1
    else:
        if match_df.iloc[index]['totalCreepScore'] == 0:
            winloss = 'Remake'
            remakeCounter1 +=1
        else:
            if match_df.iloc[index]['deaths'] == 0:
                kda += (match_df.iloc[index]['kills']+match_df.iloc[index]['assists'])/1
                winloss = 'Lose'
            else:
                kda += (match_df.iloc[index]['kills']+match_df.iloc[index]['assists'])/match_df.iloc[index]['deaths']
                winloss = 'Lose'
    
    win_history.append(winloss)
    avg_kda[0] += kda
    avg_cs[0] += cs
    wr[0] += wr1
    remakeCounter[0] += remakeCounter1