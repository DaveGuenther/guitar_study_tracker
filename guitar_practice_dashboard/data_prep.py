import pandas as pd
import numpy as np
import datetime
import pytz
import calendar

def processArsenalData(session_model, guitar_model, string_set_model):
    df_guitar_raw = guitar_model.df_raw
    df_string_raw = string_set_model.df_raw
    df_session_raw = session_model.df_raw
    df_guitar_string_raw = df_guitar_raw.merge(df_string_raw,how='left',left_on='string_set_id',right_on='id')
    df_guitar_string_raw = df_guitar_string_raw.drop('id_y',axis=1).rename({'id_x':'id'},axis=1)
    def get_string_health(df_subset, install_date):
        if df_subset.shape[0]>0:
            #install_date = df_subset['session_date'].min()
            hrs_on_strings = df_subset['duration'].sum()/60
        else:
            #install_date = None
            hrs_on_strings= 0
            
        days_on_strings=(datetime.date.today()-install_date).days
        string_health = 1-max((hrs_on_strings/60),(days_on_strings/112))
        decay_slope = (string_health-1)/(days_on_strings-0)
        expected_string_expiration_duration = int(-1/decay_slope)-days_on_strings
        expiration_date = datetime.date.today()+datetime.timedelta(days=expected_string_expiration_duration)

        return pd.Series([hrs_on_strings,
                         days_on_strings,
                         string_health,
                         expected_string_expiration_duration,
                         expiration_date])
    
    df_guitar_string_raw[['hours_on_strings',
                          'days_on_strings',
                          'string_health',
                          'expected_days_left',
                          'expiration_date']] = df_guitar_string_raw.apply(lambda row: get_string_health(df_session_raw[
                              (df_session_raw['session_date']>=row['strings_install_date'])&
                              (df_session_raw['guitar_id']==row['id'])], row['strings_install_date']),axis=1)

    df_guitar_string_raw['hours_on_guitar'] = df_guitar_string_raw.apply(lambda row: df_session_raw[df_session_raw['guitar_id']==row['id']]['duration'].sum()/60, axis=1)
    df_guitar_string_raw = df_guitar_string_raw.sort_values('hours_on_guitar', ascending=False)
    
    return df_guitar_string_raw

def processData(session_data, arrangement_data, song_data, artist_data, style_data):

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
    df_raw_arrangement = arrangement_data.df_raw
    df_raw_artist = artist_data.df_raw
    df_raw_style = style_data.df_raw
    df_raw_song = song_data.df_raw

    df_raw_song['style_id'] = df_raw_song['style_id'].astype("Int64") # Allows us to join on null ints since this column is nullable
    df_raw_song['composer_id'] = df_raw_song['composer_id'].astype("Int64") # Allows us to join on null ints since this column is nullable
    df_raw_arrangement['arranger'] = df_raw_arrangement['arranger'].astype("Int64") # Allows us to join on null ints since this column is nullable

    df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id','name':'composer'},axis=1)
    df_resolved_song = df_resolved_song.merge(df_raw_style, how='left', left_on='style_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)

    df_raw_artist['last_name']=df_raw_artist['name'].str.split(' ').str[-1] # name is spelled "first last"
        
    df_resolved_arrangement = df_raw_arrangement.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y','last_name'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
    df_resolved_arrangement = df_resolved_arrangement.merge(df_resolved_song, how='left',left_on='song_id',right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)
    #df_resolved_arrangement = df_resolved_arrangement.merge(df_raw_artist, how='left', left_on='composer', right_on='id').drop(['composer','id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
    #df_resolved_arrangement = df_resolved_arrangement.merge(df_raw_style, how='left', left_on='style_id', right_on='id').drop(['style_id','id_y'], axis=1).rename({'id_x':'id', 'style':'Style'},axis=1)
    df_resolved_arrangement['Start Date'] = pd.to_datetime(df_resolved_arrangement['start_date']).dt.strftime("%m/%d/%Y")
    df_resolved_arrangement['Off Book Date'] = pd.to_datetime(df_resolved_arrangement['off_book_date']).dt.strftime("%m/%d/%Y")
    df_resolved_arrangement['Play Ready Date'] = pd.to_datetime(df_resolved_arrangement['play_ready_date']).dt.strftime("%m/%d/%Y")
    df_resolved_arrangement = df_resolved_arrangement.rename({'title':'Title'},axis=1)
    df_resolved_sessions = df_raw_session.merge(df_resolved_arrangement,how='left', left_on='l_arrangement_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)
    
    # Establish empty records for every day in the past 365 days to serve as a scaffold for the heatmap table - in the event that all data is filtered out, the structure will be retained
    df_zeros = pd.DataFrame({'session_date':pd.date_range(today-pd.DateOffset(days=365),today),'duration':np.zeros(len(pd.date_range(today-pd.DateOffset(days=365),today)))})
    df_resolved_sessions['session_date'] = pd.to_datetime(df_resolved_sessions['session_date'])
    df_resolved_sessions = pd.concat([df_resolved_sessions,df_zeros]).reset_index()
    df_resolved_sessions['Session Date'] = pd.to_datetime(df_resolved_sessions['session_date']).dt.strftime("%m/%d/%Y")
    df_resolved_sessions = df_resolved_sessions.rename({'style':'Style','composer':'Composer','duration':'Duration','notes':'Notes','Title':'Song','stage':'Stage','video_url':'Video URL','song_type':'Song Type'},axis=1)
    
    # Collect date parts of the session_date for use in various visuals
    df_summary = df_resolved_sessions[['id', 'Session Date','session_date','Stage', 'Duration', 'Song','Song Type','Style','l_arrangement_id','Composer','Arranger','Notes', 'Video URL']].sort_values('Session Date', ascending=False)
    #df_summary['URL_provided'] = df_summary['Video URL'].apply(lambda observation: True if observation else False)
    df_summary['session_date'] = pd.to_datetime(df_summary['session_date'])
    df_summary['Year'] = df_summary['session_date'].dt.isocalendar().year
    df_summary['Week'] = df_summary['session_date'].dt.isocalendar().week
    df_summary['weekday_number'] = df_summary['session_date'].dt.weekday
    df_weekdays = pd.DataFrame(
        {'weekday_number':[0,1,2,3,4,5,6],
         'Weekday':['Monday','Tuesday','Wedensday','Thursday','Friday','Saturday','Sunday'],
         'Weekday_abbr':['Mon','Tue','Wed','Thu','Fri','Sat','Sun']})
    df_summary = df_summary.merge(df_weekdays, how='left', on='weekday_number')
    df_summary['week_start'] = df_summary.apply(lambda row: pd.to_datetime(str(row['Week'])+str(row['Year'])+'Mon', format='%W%Y%a'),axis=1) #pd.to_datetime(df_summary['Week'].astype(str)+str('2024')+'Sun', format='%W%Y%a')
    df_summary['week_start_day_num'] = df_summary['week_start'].dt.day
    df_summary['month_abbr'] = df_summary.apply(lambda row: str(row['week_start'].strftime('%b')),axis=1)
    df_summary['month_year'] = df_summary.apply(lambda row: str(row['week_start'].strftime('%b'))+" '"+str(row['week_start'].strftime('%y')),axis=1)
    df_summary['month_week_start'] = df_summary.apply(lambda row: str(row['week_start'].strftime('%b'))+" "+str(row['week_start'].strftime('%d')),axis=1)
    df_summary['week_end'] = df_summary['week_start']+ pd.Timedelta(days=6)
    df_summary['week_str'] = df_summary.apply(lambda row: str(row['week_start'].strftime('%b %d'))+" - "+str(row['week_end'].strftime('%b %d')),axis=1)
    df_summary['Video URL'] = df_summary['Video URL'].replace({np.nan: None})

    # Imputing missing values
    df_summary['Duration'] = df_summary['Duration'].fillna(0)
    df_summary['Composer'] = df_summary['Composer'].fillna("Unknown")
    df_summary['Arranger'] = df_summary['Arranger'].fillna("Unknown")

    df_365 = df_summary[df_summary['session_date']>=today-pd.DateOffset(days=365)] # for the 365 day heatmap
    df_summary=df_summary[df_summary['id'].notna()] #for the cumulative data since inception
    return df_summary, df_365

def processArrangementGrindageData(session_model, arrangement_model, song_model, artist_model, style_model):
    #df_arrangements = arrangement_model.df_raw
    #df_sessions = df_sessions[df_sessions['Song Type']=='Song']

    #df_sessions_expanded = df_sessions.merge(df_arrangements[['id','start_date','off_book_date','at_tempo_date','play_ready_date']], how='left', left_on='l_arrangement_id', right_on='id').drop('id_y',axis=1).rename({'id_x':'id'},axis=1)
    df_raw_session = session_model.df_raw
    df_raw_arrangement = arrangement_model.df_raw
    df_raw_song = song_model.df_raw
    df_raw_artist = artist_model.df_raw
    df_raw_style = style_model.df_raw
    df_raw_song['style_id'] = df_raw_song['style_id'].astype("Int64") # Allows us to join on null ints since this column is nullable
    df_raw_song['composer_id'] = df_raw_song['composer_id'].astype("Int64") # Allows us to join on null ints since this column is nullable
    
    df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id','name':'composer'},axis=1)
    df_resolved_song = df_resolved_song.merge(df_raw_style, how='left', left_on='style_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)

    df_resolved_arrangement = df_raw_arrangement.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y','last_name'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
    df_resolved_arrangement = df_resolved_arrangement.merge(df_resolved_song, how='left',left_on='song_id',right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)
    
    df_grindage = df_raw_session.groupby(['l_arrangement_id','stage'])[['duration']].sum().reset_index()
    df_grindage = df_grindage.merge(df_resolved_arrangement, how='left',left_on='l_arrangement_id',right_on='id')
    today = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
    df_grindage['today']= today
    def getStageStartDates(row):
        date_ref = {
            'Learning Notes':'start_date',
            'Achieving Tempo':'off_book_date',
            'Phrasing':'at_tempo_date',
            'Maintenance':'play_ready_date'
        }
        return row[date_ref[row['stage']]]

    def getStageEndDates(row):
        date_ref = {
            'Learning Notes':'off_book_date',
            'Achieving Tempo':'at_tempo_date',
            'Phrasing':'play_ready_date',
            'Maintenance':'today'
        }
        return row[date_ref[row['stage']]]

    df_grindage['Start Date'] = df_grindage.apply(getStageStartDates, axis=1)
    df_grindage['End Date'] = df_grindage.apply(getStageEndDates, axis=1)
    df_grindage['End Date'] = df_grindage['End Date'].fillna(today)
    df_grindage = df_grindage.rename({'stage':'Stage','duration':'Duration','title':'Title','composer':'Composer','arranger':'Arranger','song_type':'Song Type'},axis=1)
    df_grindage = df_grindage[['Stage','Duration','id','Title','Composer','Arranger','Song Type','Start Date','End Date']]
    return df_grindage

def processSongGoalsData(arrangement_model, arrangement_goal_model, song_model, artist_model, style_model):
    df_raw_arrangement_goals = arrangement_goal_model.df_raw
    df_raw_arrangement = arrangement_model.df_raw    
    df_raw_song = song_model.df_raw
    df_raw_artist = artist_model.df_raw
    df_raw_style = style_model.df_raw
    
    df_raw_song['style_id'] = df_raw_song['style_id'].astype("Int64") # Allows us to join on null ints since this column is nullable
    df_raw_song['composer_id'] = df_raw_song['composer_id'].astype("Int64") # Allows us to join on null ints since this column is nullable
    df_raw_arrangement['arranger'] = df_raw_arrangement['arranger'].astype("Int64") # Allows us to join on null ints since this column is nullable
        
    df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id','name':'composer'},axis=1)
    df_resolved_song = df_resolved_song.merge(df_raw_style, how='left', left_on='style_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)
    
    df_resolved_arrangement = df_raw_arrangement.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y','last_name'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
    df_resolved_arrangement = df_resolved_arrangement.merge(df_resolved_song, how='left', left_on='song_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)
    
    df_resolved_arrangement_goals = df_raw_arrangement_goals.merge(df_resolved_arrangement, how='inner', left_on='arrangement_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)    
    df_resolved_arrangement_goals = df_resolved_arrangement_goals[df_resolved_arrangement_goals['song_type']=='Song'].copy()
    df_resolved_arrangement_goals = df_resolved_arrangement_goals.rename({'discovery_date':'Discovery Date','description':'Description','difficulty':'Difficulty','sheet_music_link':'Sheet Music Link', 'performance_link':'Performance Link','title':'Title','song_type':'Song Type','composer':'Composer','style':'Style'},axis=1)
    df_resolved_arrangement_goals = df_resolved_arrangement_goals[['id','song_id','Discovery Date','Description','Difficulty','Sheet Music Link','Performance Link','Arranger','Title','Song Type','Composer','Style']]
    df_resolved_arrangement_goals['id'] = df_resolved_arrangement_goals['id'].astype(str)
    df_resolved_arrangement_goals['song_id'] = df_resolved_arrangement_goals['song_id'].astype(str)
    return df_resolved_arrangement_goals.copy()


