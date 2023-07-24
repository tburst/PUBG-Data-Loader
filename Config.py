import json
import sqlite3
from sqlite3 import Error

relevant_player_list = [] # list of players to be tracked

account_id_dict = {}  #dictionary of playername: account id mapping for relevant players

#time definitions for first/second weapon variables
start_interval = 60
end_interval = 1800
interval_iteration = 120
weapon_one_pick_drop_columns = {f"Weapon_One_Min_{int(time_interval/60)}": "TEXT" for time_interval in range(start_interval,end_interval ,interval_iteration)}
weapon_two_pick_drop_columns = {f"Weapon_Two_Min_{int(time_interval/60)}": "TEXT" for time_interval in range(start_interval,end_interval ,interval_iteration)}

#map readable item names to item entries
with open("assets\\itemId.json") as read_file:
    item_meta_dict = json.load(read_file)
    item_meta_dict['Item_Weapon_Julies_Kar98k_C'] = "Kar98k"  #convert special item names to general versions
    item_meta_dict['Item_Weapon_Lunchmeats_AK47_C'] = "AKM"

sql_path = "transformed_data\\pubg.db"

participant_columns = {"match_id": "TEXT",
                       "createdAt": "TEXT",
                       "duration": "INTEGER",
                       "mapName": "TEXT",
                       "gameMode": "TEXT",
                       "player_id": "TEXT",
                       "player_name": "TEXT",
                       "participant_id": "TEXT",
                       "DBNOs": "INTEGER",
                       "assists": "INTEGER",
                       "boosts": "INTEGER",
                       "damageDealt": "REAL",
                       "deathType": "TEXT",
                       "headshotKills": "INTEGER",
                       "heals": "INTEGER",
                       "killPlace": "INTEGER",
                       "killStreaks": "INTEGER",
                       "kills": "INTEGER",
                       "longestKill": "REAL",
                       "revives": "INTEGER",
                       "rideDistance": "REAL",
                       "roadKills": "INTEGER",
                       "swimDistance": "REAL",
                       "teamKills": "INTEGER",
                       "timeSurvived": "INTEGER",
                       "vehicleDestroys": "INTEGER",
                       "walkDistance": "REAL",
                       "weaponsAcquired": "INTEGER",
                       "winPlace": "INTEGER",
                       "landing_location_x": "REAL",
                       "landing_location_y": "REAL",
                       "landing_location_zone": "TEXT",
                       ** weapon_one_pick_drop_columns,
                       ** weapon_two_pick_drop_columns,
                       ** {f"{player_name}_participated": "INTEGER" for player_name in relevant_player_list}}


map_size_dict = {"Erangel": 816000,
                 "Miramar": 816000,
                 "Vikendi": 612000,
                 "Sanhok":  408000,
                 "Taego":   816000,
                 "Karakin": 204000}


map_dict = {
  "Baltic_Main": "Erangel",
  "Chimera_Main": "Paramo",
  "Desert_Main": "Miramar",
  "DihorOtok_Main": "Vikendi",
  "Erangel_Main": "Erangel",
  "Heaven_Main": "Haven",
  "Range_Main": "Camp Jackal",
  "Savage_Main": "Sanhok",
  "Summerland_Main": "Karakin",
  "Tiger_Main": "Taego"
}


#helper script for sql connection

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn