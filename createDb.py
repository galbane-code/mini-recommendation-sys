import sqlite3 as lite
import pandas as pd


def change_df_cols(df, col_names):
    df_col_names = list(df.columns)
    zip_iterator = zip(df_col_names, col_names)
    dict_cols = dict(zip_iterator)
    return df.rename(columns=dict_cols)


if __name__ == '__main__':
    # first step is to separate the data to specific tables

    df = pd.read_csv("BikeShare.csv")
    col_names = list(df.columns)
    trip_final_index = col_names.index("EndStationID") + 1
    trip_table = df.iloc[:, :trip_final_index].drop(
        columns=['StartStationName', 'StartStationLongitude', 'StartStationLatitude'])
    station_start_table = df[['StartStationID', 'StartStationName', 'StartStationLatitude',
                              'StartStationLongitude']]
    station_end_table = df[['EndStationID', 'EndStationName', 'EndStationLatitude',
                            'EndStationLongitude']]
    bike_table = df[['BikeID', 'UserType', 'BirthYear', 'Gender', 'TripDurationinmin']]

    station_merged_col_names = ['StationID', 'StationName', 'StationLatitude',
                                'StationLongitude']

    station_start_table = change_df_cols(station_start_table, station_merged_col_names)
    station_end_table = change_df_cols(station_end_table, station_merged_col_names)

    frames = [station_start_table, station_end_table]
    station_merged_table = pd.concat(frames).drop_duplicates()

    # the second step is to create the db and the db tables

    con = lite.connect('test.db')
    with con:
        cur = con.cursor()
        ###################################################################################################################################################
        ## CREATE THE DB TABLES

        cur.execute('''CREATE TABLE IF NOT EXISTS TRIP_DETAILS
                      (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                       TRIP_DURRATION INTEGER ,
                       START_TIME DATETIME,
                       STOP_TIME DATETIME,
                       START_STATION_ID INTEGER ,
                       STOP_STATION_ID INTEGER 
                       )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS STATION_DETAILS
                      (STATION_ID INTEGER PRIMARY KEY,
                       STATION_NAME NVARCHAR(100) ,
                       STATION_LATITUDE REAL,
                       STATION_LONGITUDE REAL
                       )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS BIKE_DETAILS
                      (BIKE_ID INTEGER,
                       USER_TYPE NVARCHAR(100) ,
                       BIRTH_YEAR INTEGER,
                       GENDER BOOLEAN,
                       TRIP_DURATION_IN_MIN INTEGER ,
                       TRIP_ID INTEGER
                       )''')

        ##################################################################################################################################################

        # the third step is to load the data into the tables from the data frames
        # insert to the trip details table
        # self.cursor.execute("SELECT weight FROM Equipment WHERE name = ?", [item]) example

        for row in trip_table.iterrows():
            cur.execute('''
                            INSERT INTO TRIP_DETAILS (TRIP_DURRATION, START_TIME, STOP_TIME, START_STATION_ID, STOP_STATION_ID)
                            VALUES( ?,	? , ? , ?, ?);
                            ''', [row[1]["TripDuration"], row[1]["StartTime"], row[1]["StopTime"],
                                  row[1]["StartStationID"], row[1]["EndStationID"]])

        for row in station_merged_table.iterrows():
            cur.execute('''
                            INSERT INTO STATION_DETAILS (STATION_ID, STATION_NAME, STATION_LATITUDE, STATION_LONGITUDE)
                            VALUES( ?,	? , ? , ?);
                            ''', [row[1]["StationID"], row[1]["StationName"], row[1]["StationLatitude"],
                                  row[1]["StationLongitude"]])


        trip_id = 1
        for row in bike_table.iterrows():
            cur.execute('''
                            INSERT INTO BIKE_DETAILS (BIKE_ID, USER_TYPE, BIRTH_YEAR, GENDER, TRIP_DURATION_IN_MIN, TRIP_ID)
                            VALUES( ?,	? , ? , ?, ?, ?);
                            ''', [row[1]["BikeID"], row[1]["UserType"], row[1]["BirthYear"],
                                  row[1]["Gender"], row[1]["TripDurationinmin"], trip_id])
            trip_id += 1