import numpy as np
import pandas as pd

# AB = O+E+K+S+D+T+HR
# PA = O+E+K+BB+IBB+HBP+I+S+D+T+HR

LINEAR_WEIGHTS = ['BB','HBP','S','D','T','HR']

def calc_woba_weights(oba,mlb):
    """
    oba: instance of wOBAWeightSim
    mlb: instance of BattingSim
    -----------------------------------------
    returns: DataFrame with columns [woba,woba_Scale,BB,HBP,S,D,T,HR]
    """
    # Calc adjusted linear weights
    adjlw = oba.adjWeights()
    # League OBP (On Base Percentage)
    obp = mlb['(S+D+T+HR+BB+HBP)/(O+E+K+S+D+T+HR+BB+HBP+SF)']
    # League wOBA
    woba = (mlb[LINEAR_WEIGHTS]*adjlw[LINEAR_WEIGHTS].values).sum(axis=1,keepdims=True)/mlb['O+E+K+S+D+T+HR+BB+SF+HBP']
    # wOBA Scale
    woba_scale = obp / woba
    # Final wOBA linear weights
    lw = adjlw.values * woba_scale
    return pd.DataFrame(np.c_[woba,woba_scale,lw],index=mlb.index.pandas(),columns=['woba','woba_Scale','BB','HBP','S','D','T','HR'])

def calc_woba(batting,lw):
    inx = list(batting.index.names)
    # creates a map of lw to batting data
    lwmap = pd.merge(batting.reset_index()[inx],lw.reset_index(),how='left',on=['year']).set_index(inx)
    woba = ((batting[LINEAR_WEIGHTS]*lwmap[LINEAR_WEIGHTS]).sum(axis=1)/batting[['O', 'E', 'K', 'S', 'D', 'T', 'HR','BB','HBP','SF']].sum(axis=1))
    pa = batting[['O','E','K','BB','IBB','HBP','I','S','D','T','HR']].sum(axis=1).rename('pa').to_frame()
    return pd.merge(woba.replace([np.inf, -np.inf], np.nan).rename('woba').to_frame(),pa,how='inner',left_index=True,right_index=True)

def _calc_wraa(stats,woba,woba_scale,lw):
    for y,group in stats.groupby('year'):
        gwoba = ((group[['BB','HBP','S','D','T','HR']]*lw.loc[y]).sum(axis=1)/group[['O','E','K','S','D','T','HR','BB','HBP','SF']].sum(axis=1)).replace([np.inf, -np.inf], np.nan)
        yield (gwoba / woba_scale.loc[y] - woba.loc[y]).rename('wRAA')

def calc_war_battingfactor(oba,mlb,league,parkfactor,batting):
    """
    oba: instance of wOBAWeightSim
    mlb: instance of BattingSim
    league: DataFrame
    parkfactor: DataFrame
    batting: DataFrame
    -----------------------------------------
    returns: DataFrame with column [BattingFactor]
    """
    # calculate wOBA
    woba = calc_woba_weights(oba,mlb)

    # Calculate Runs/Plate Appearance
    rpa = pd.Series(np.r_[(*mlb['R/(O+E+K+BB+IBB+HBP+I+S+D+T+HR)'],)],index=mlb.index.pandas(),name='RPA')
    # Calculate weighted park factor
    wPF = (1 - (parkfactor / 100)).groupby('team').apply(lambda x: x * rpa).rename('wPF').to_frame()

    # Calculate np_league wOBA
    lw = woba[LINEAR_WEIGHTS]
    np_woba = (league[LINEAR_WEIGHTS].groupby('league').apply(lambda x: x * lw)).sum(axis=1) / league[['O','E','K','S','D','T','HR','BB','SF','HBP']].sum(axis=1)
    # Calculate modified wRC for np-league
    wLG = np_woba.groupby('league').apply(lambda x: -(x/woba['woba_Scale'] - woba['woba'])).rename('wLG').to_frame()
    # calc wRAA
    wRAA = pd.concat([*_calc_wraa(batting,woba['woba'],woba['woba_Scale'],lw)],axis=0).to_frame()
    # calc batting PA
    pa = batting[['O','E','K','BB','IBB','HBP','I','S','D','T','HR']].sum(axis=1).rename('pa').to_frame()
    # Merge PA, wRAA, wPF, wLG into one frame
    bf = pd.merge(pa,wRAA,how='inner',left_index=True,right_index=True).reset_index()
    bf = pd.merge(bf,wPF,how='left',left_on=['year','team'],right_on=['year','team'])
    bf = pd.merge(bf,wLG,how='left',left_on=['year','league'],right_on=['year','league'])
    bf.set_index(list(batting.index.names),inplace=True)
    # Calculate Batting Factor
    batfactor = (bf['wRAA']*bf['pa']+bf['wPF']*bf['pa']+bf['wLG']*bf['pa']).rename('bf').to_frame()
    return pd.merge(batfactor,pa,how='inner',left_index=True,right_index=True)
