
import pandas as pd

def salary_data():
    return pd.read_csv('/Users/luciancooper/BBSRC/FILES/salary.csv',index_col=['year','league','team','pid'])['salary']

def team_payroll():
    salary = salary_data()
    payroll = salary.groupby(['year','league','team']).sum().rename('payroll')
    return payroll

def player_salpct():
    salary = salary_data()
    payroll = salary.groupby(['year','league','team']).sum().rename('payroll')
    salary = pd.merge(salary.reset_index(),payroll.to_frame(),how='left',left_on=['year','league','team'],right_index=True)
    salary.set_index(['year','league','team','pid'],inplace=True)
    return (salary['salary']/salary['payroll']).rename('salarypct')
