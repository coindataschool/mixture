import os
import pandas as pd
from duneanalytics import DuneAnalytics

def extract_frame_from_dune_data(dune_data, date_col='day'):    
    dd = dune_data['data']['get_result_by_result_id']
    df = pd.json_normalize(dd, record_prefix='')
    df = df.loc[:, df.columns.str.startswith('data')]
    df.columns = df.columns.str.replace('data.', '', regex=False)
    df['date'] = pd.to_datetime(df[date_col].str.replace('T.*', '', regex=True))
    if date_col != 'date':
        df = df.drop(date_col, axis=1)
    df = df.set_index('date').sort_index()
    # drop the last row cuz it may not always be a full day
    return df.iloc[:-1, :]

# get Dune Analytics login credentials
MY_USERNAME = os.environ.get('DUNE_USERNAME')
MY_PASSWORD = os.environ.get('DUNE_PASSWORD')
dune = DuneAnalytics(MY_USERNAME, MY_PASSWORD)

dune.login()
dune.fetch_auth_token()
