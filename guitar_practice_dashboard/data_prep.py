import pandas as pd
import numpy as np
import datetime
import pytz
import calendar

def processData(session_data, song_data, artist_data, style_data):

    def get_week_number(date):
        # Set the first day of the week to Sunday
        calendar.setfirstweekday(calendar.SUNDAY)

        # Get the ISO week number (weeks start on Monday)
        iso_week_number = date.isocalendar().week

        # Adjust if the first week of the year starts on Sunday
        if date.weekday() == 6 and iso_week_number == 1:
            return 1
        elif date.weekday() == 6:
            return iso_week_number + 1
        else:
            return iso_week_number
    today = datetime.datetime.now(pytz.timezone('US/Eastern')).date()

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
    df_zeros = pd.DataFrame({'Date':pd.date_range(today-pd.DateOffset(days=365),today),'Dur':np.zeros(len(pd.date_range(today-pd.DateOffset(days=365),today)))})
    df_resolved_sessions['session_date'] = pd.to_datetime(df_resolved_sessions['session_date'])
    df_resolved_sessions = df_zeros.merge(df_resolved_sessions,how='left',left_on='Date',right_on='session_date')
    df_resolved_sessions['duration'] = df_resolved_sessions.apply(lambda row: 0 if pd.isna(row['session_date']) else row['duration'], axis=1)
    df_resolved_sessions['session_date']=df_resolved_sessions['Date']
    df_resolved_sessions.drop(['Date','Dur'],axis=1)
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
    #df_summary['Week'] = df_summary.apply(lambda row: get_week_number(row['session_date']), axis=1) # Week number adjusted to start on Sunday, not Monday
    df_summary['week_start'] = df_summary.apply(lambda row: pd.to_datetime(str(row['Week'])+str(row['Year'])+'Mon', format='%W%Y%a'),axis=1) #pd.to_datetime(df_summary['Week'].astype(str)+str('2024')+'Sun', format='%W%Y%a')
    df_summary['week_start_day_num'] = df_summary['week_start'].dt.day
    df_summary['month_abbr'] = df_summary.apply(lambda row: str(row['week_start'].strftime('%b')),axis=1)
    df_summary['month_year'] = df_summary.apply(lambda row: str(row['week_start'].strftime('%b'))+" '"+str(row['week_start'].strftime('%y')),axis=1)
    df_summary['month_week_start'] = df_summary.apply(lambda row: str(row['week_start'].strftime('%b'))+" "+str(row['week_start'].strftime('%d')),axis=1)
    df_summary['week_end'] = df_summary['week_start']+ pd.Timedelta(days=6)
    df_summary['week_str'] = df_summary.apply(lambda row: str(row['week_start'].strftime('%b %d'))+" - "+str(row['week_end'].strftime('%b %d')),axis=1)
    df_summary['Video URL'] = df_summary['Video URL'].replace({np.nan: None})
    df_summary['Duration'] = df_summary['Duration'].fillna(0)
    df_grouped_by_date = df_summary.groupby('session_date') # grouped by date in order to capture an '*' if ANY recording weas posted that day
    df_summary['has_url'] = df_grouped_by_date['Video URL'].transform(lambda group: '*' if any(group.values) else'')
    df_365 = df_summary[df_summary['session_date']>=today-pd.DateOffset(days=365)]
    df_summary=df_summary[df_summary['id'].notna()]
    return df_summary, df_365