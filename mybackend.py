import sqlite3 as lite
import pandas as pd
from math import radians, cos, sin, asin, sqrt

con = lite.connect('recommendation.db')

def change_df_cols(df, col_names):
    """
    The function receives the Dataframe and the new col names to replace
    The existing col names that are in the Dataframe
    """
    df_col_names = list(df.columns)
    zip_iterator = zip(df_col_names, col_names)
    dict_cols = dict(zip_iterator)
    return df.rename(columns=dict_cols)


def check_db_table_exists(cur, table_name):
    """
    The function checks if the a table have any records
    """
    cur.execute('SELECT * FROM ' + table_name)
    table = cur.fetchall()
    return len(table) == 0


def check_location_in_db(location_name):
    """
    The function checks if a specific location exists in the station details table
    """
    con = lite.connect('recommendation.db')
    with con:
        cur = con.cursor()
        cur.execute('''
                    SELECT *
                    FROM STATION_DETAILS
                    WHERE STATION_NAME = ?
                    ''', [location_name.lower()])
        ret_val = cur.fetchall()
        return len(ret_val) > 0


def get_location_for_recommendation(start_location, time_of_trip, num_of_recommendation):
    """
    The main function of our recommendation-sys, it receives the start location
    and the time of the user desires and the number of recommendations he wants
    """

    con = lite.connect('recommendation.db')
    with con:
        from_table = '''
                         FROM TRIP_DETAILS TP
        						 JOIN STATION_DETAILS SD2 ON SD2.STATION_ID = TP.START_STATION_ID
        						 WHERE SD2.STATION_NAME = ?
        						 GROUP BY TP.STOP_STATION_ID
        						 HAVING TRIP_DURRATION_IN_MIN <= ?
        						 ORDER BY TRIP_DURRATION_IN_MIN ASC, TP.TRIP_DISTANCE ASC
                            ) AS TP ON SD1.STATION_ID = TP.STOP_STATION_ID
                        '''
        cur = con.cursor()
        cur.execute('''
                               SELECT SD1.STATION_NAME
                                FROM STATION_DETAILS SD1
                                JOIN (SELECT TP.STOP_STATION_ID, (SELECT TRIP_DURRATION_IN_MIN
                                        FROM TRIP_DETAILS
                                        ORDER BY TRIP_DURRATION_IN_MIN
                                        LIMIT 1
                                        OFFSET (SELECT COUNT(*)
                                        FROM TRIP_DETAILS) / 2) AS TRIP_DURRATION_IN_MIN 

                                ''' + from_table, [start_location.lower(), time_of_trip])

        locations_table = cur.fetchall()
        if len(locations_table) == 0:
            cur.execute('''
                           SELECT SD1.STATION_NAME
                            FROM STATION_DETAILS SD1
                            JOIN (SELECT TP.STOP_STATION_ID, MIN(TP.TRIP_DURRATION_IN_MIN) AS TRIP_DURRATION_IN_MIN
                            ''' + from_table, [start_location.lower(), time_of_trip])
            locations_table = cur.fetchall()

        locations_table = [item[0] for item in locations_table]
        locations_table = locations_table[0:num_of_recommendation]
        return locations_table


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


if __name__ == '__main__':
    # first step is to separate the data to specific tables
    df = pd.read_csv("BikeShare.csv")
    col_names = list(df.columns)
    trip_final_index = col_names.index("EndStationLongitude") + 1
    trip_table = df[['TripDurationinmin', 'StartStationID', 'EndStationID']]
    dist_df = df[['StartStationLatitude', 'StartStationLongitude', 'EndStationLatitude', 'EndStationLongitude']]
    station_start_table = df[['StartStationID', 'StartStationName']]
    station_end_table = df[['EndStationID', 'EndStationName']]
    trip_dist_col = dist_df.apply(lambda row: haversine(row['StartStationLatitude'],
                                                        row['StartStationLongitude'],
                                                        row['EndStationLatitude'],
                                                        row['EndStationLongitude']), axis=1).tolist()
    trip_table.insert(3, "trip_dist", trip_dist_col)
    station_merged_col_names = ['StationID', 'StationName']

    station_start_table = change_df_cols(station_start_table, station_merged_col_names)
    station_end_table = change_df_cols(station_end_table, station_merged_col_names)

    frames = [station_start_table, station_end_table]
    station_merged_table = pd.concat(frames).drop_duplicates()
    station_merged_table["StationName"] = station_merged_table["StationName"].str.lower()

    # the second step is to create the db and the db tables

    with con:
        cur = con.cursor()
        ###################################################################################################################################################
        ## CREATE THE DB TABLES

        cur.execute('''CREATE TABLE IF NOT EXISTS TRIP_DETAILS
                      (
                       START_STATION_ID INTEGER ,
                       STOP_STATION_ID INTEGER ,
                        TRIP_DURRATION_IN_MIN INTEGER,
                        TRIP_DISTANCE REAL
                       )''')

        cur.execute('''CREATE TABLE IF NOT EXISTS STATION_DETAILS
                      (STATION_ID INTEGER PRIMARY KEY,
                       STATION_NAME NVARCHAR(100) 
                       )''')

        ##################################################################################################################################################

        # the third step is to load the data into the tables from the data frames
        # insert to the trip details table

        is_trip_details_exists = check_db_table_exists(cur, 'TRIP_DETAILS')
        is_station_details_exists = check_db_table_exists(cur, 'STATION_DETAILS')
        trip_table = change_df_cols(trip_table, ['TRIP_DURRATION_IN_MIN', 'START_STATION_ID', 'STOP_STATION_ID',
                                                 'TRIP_DISTANCE'])
        station_merged_table = change_df_cols(station_merged_table, ['STATION_ID', 'STATION_NAME'])

        if is_trip_details_exists:
            trip_table.to_sql("TRIP_DETAILS", con, if_exists='append', index=False)

        if is_station_details_exists:
            station_merged_table.to_sql("STATION_DETAILS", con, if_exists='append', index=False)
