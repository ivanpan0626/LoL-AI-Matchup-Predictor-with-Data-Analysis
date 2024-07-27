

#Converts gameDuration to minute/seconds
def test(chal_df, summonerGameNames, summonerTagLines, summonerIcons, summonerLevels):
    chal_df_new = chal_df[['leaguePoints', 'hotStreak']]
    chal_df_new.insert(0, 'summonerGameName', summonerGameNames)
    chal_df_new.insert(1, 'summonerTagLine', summonerTagLines)
    chal_df_new.insert(2, 'win_rate', (chal_df['wins']/(chal_df['wins']+chal_df['losses'])).apply('{:.0%}'.format))
    chal_df_new.insert(3, 'winloss', chal_df['wins'].astype(str) + '/' + chal_df['losses'].astype(str))
    chal_df_new.insert(4, 'profileIconId', summonerIcons)
    chal_df_new.insert(5, 'summonerLevel', summonerLevels)
    leaderboard = chal_df_new.to_dict(orient='records')

    return leaderboard