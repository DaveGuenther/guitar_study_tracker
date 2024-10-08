import pandas as pd

def processData(session_data, song_data, artist_data, style_data):
    print("Hello World")
    df_raw_session = session_data.df_raw
    df_raw_song = song_data.df_raw
    df_raw_artist = artist_data.df_raw
    df_raw_style = style_data.df_raw
    df_raw_artist['last_name']=df_raw_artist['name'].str.split(' ').str[-1] # name is spelled "first last"
    df_raw_song['style_id'] = df_raw_song['style_id'].astype("Int64") # Allows us to join on null ints since this column is nullable
    df_raw_song['composer'] = df_raw_song['composer'].astype("Int64") # Allows us to join on null ints since this column is nullable
    df_raw_song['arranger'] = df_raw_song['arranger'].astype("Int64") # Allows us to join on null ints since this column is nullable
    df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y','last_name'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
    df_resolved_song = df_resolved_song.merge(df_raw_artist, how='left', left_on='composer', right_on='id').drop(['composer','id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
    df_resolved_song = df_resolved_song.merge(df_raw_style, how='left', left_on='style_id', right_on='id').drop(['style_id','id_y'], axis=1).rename({'id_x':'id', 'style':'Style'},axis=1)
    df_resolved_song['Start Date'] = pd.to_datetime(df_resolved_song['start_date']).dt.strftime("%m/%d/%Y")
    df_resolved_song['Off Book Date'] = pd.to_datetime(df_resolved_song['off_book_date']).dt.strftime("%m/%d/%Y")
    df_resolved_song['Play Ready Date'] = pd.to_datetime(df_resolved_song['play_ready_date']).dt.strftime("%m/%d/%Y")
    df_resolved_song = df_resolved_song.rename({'title':'Title'},axis=1)
    df_resolved_sessions = df_raw_session.merge(df_resolved_song,how='left', left_on='l_song_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)
    df_resolved_sessions['Session Date'] = pd.to_datetime(df_resolved_sessions['session_date']).dt.strftime("%m/%d/%Y")
    df_resolved_sessions = df_resolved_sessions.rename({'duration':'Duration','notes':'Notes','Title':'Song','video_url':'Video URL'},axis=1)
    df_summary = df_resolved_sessions[['id', 'Session Date','session_date', 'Duration', 'Song','Style','l_song_id','Composer','Arranger','Notes', 'Video URL']].sort_values('Session Date', ascending=False)
    df_summary['URL_provided'] = df_summary['Video URL'].apply(lambda observation: True if observation else False)
    df_summary['session_date'] = pd.to_datetime(df_summary['session_date'])
    df_summary['Year'] = df_summary['session_date'].dt.isocalendar().year
    df_summary['Week'] = df_summary['session_date'].dt.isocalendar().week
    df_summary['weekday_number'] = df_summary['session_date'].dt.weekday
    df_weekdays = pd.DataFrame(
        {'weekday_number':[0,1,2,3,4,5,6],
         'Weekday':['Monday','Tuesday','Wedensday','Thursday','Friday','Saturday','Sunday'],
         'Weekday_abbr':['Mon','Tue','Wed','Thu','Fri','Sat','Sun']})
    df_summary = df_summary.merge(df_weekdays, how='left', on='weekday_number')

    return df_summary