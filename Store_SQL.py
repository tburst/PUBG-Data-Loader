import os
import json

#local imports
import Transform_Raw_Data
import Config


def store_participant_data(conn,participant_data_dict) -> int
    '''
    store participant data in sql database

    Args:
        conn (sqlite3.connect): connection to the sql database
        participant_data_dict (dict): participant data to be stored

    Returns:
        int: the last row id of the inserted data
    '''
    insert_statement = f" INSERT OR REPLACE INTO participant({','.join(Config.participant_columns.keys())})" \
                       f"VALUES (?{',?'*(len(Config.participant_columns)-1)});"
    participant_data = [participant_data_dict[column] for column in Config.participant_columns]
    cur = conn.cursor()
    cur.execute(insert_statement,participant_data)
    conn.commit()

    return cur.lastrowid

if __name__ == '__main__':
    conn = Config.create_connection(Config.sql_path)
    cur = conn.cursor()
    #get all match_id and player_name combinations already stored in the database
    cur.execute("SELECT match_id, player_name FROM participant")
    match_id_player_name_list = [row for row in cur.fetchall()]
    #loop over stored json data files and extract match data for relevant players
    file_list = os.listdir("raw_data\\matches")
    for file in file_list:
        match_id = file.replace(".txt","")
        with open("raw_data\\matches\\" + file) as read_file:
            json_match_data = json.load(read_file)
        with open("raw_data\\telemetry\\" + file) as read_file:
            json_telemetry_data = json.load(read_file)
        participant_dict = Transform_Raw_Data.identify_relevant_participants(Config.account_id_dict, json_match_data)

        # check for teammates
        participated_dict = {}
        for player_name in Config.account_id_dict:
            if player_name in participant_dict:
                participated_dict[f"{player_name}_participated"] = 1
            else:
                participated_dict[f"{player_name}_participated"] = 0

        for participant_name in participant_dict:
            participant_id = participant_dict[participant_name]
            if (match_id,participant_name) in match_id_player_name_list:
                continue
            else:
                match_meta_data = Transform_Raw_Data.collect_match_meta_data(json_match_data)
                participant_stats = Transform_Raw_Data.collect_match_participant_stats(json_match_data, participant_id)
                location_dict = Transform_Raw_Data.collect_landing_location(json_telemetry_data, participant_name)
                weapon_pick_drop_dict = Transform_Raw_Data.collect_time_interval_weapon_equipped(json_telemetry_data, participant_name)
                final_stats_dict = {**match_meta_data, **participant_stats,**participated_dict,**location_dict,
                                    **weapon_pick_drop_dict, "match_id": match_id,"player_id":Config.account_id_dict[participant_name],
                                    "player_name": participant_name,"participant_id":participant_id }
                store_participant_data(conn, final_stats_dict)
                print(f"{match_id}___{participant_name} added")