from datetime import datetime

#local imports
import Config

def identify_relevant_participants(account_id_dict: dict, json_match_data: dict) -> dict:
    '''
    identify the participant ids of the relevant players in a match

    Args:
        account_id_dict (dict): dict to map player names and account ids
        json_match_data (dict): json data dict of a single match

    Returns:
        dict: dict to map player names and match participant ids
    '''
    participant_id_dict = {}
    for entry in json_match_data["included"]:
        if entry["type"] == "participant":
            for player in account_id_dict:
                if entry["attributes"]["stats"]["playerId"] == account_id_dict[player]:
                    participant_id_dict[player] = entry["id"]
    return participant_id_dict


def collect_match_meta_data(json_match_data: dict) -> dict:
    '''
    collect meta data from a single match json data dict

    Args:
        json_match_data (dict): json data dict of a single match

    Returns:
        dict: dict of match meta data
    '''
    return {"createdAt": json_match_data["data"]["attributes"]["createdAt"],
            "mapName": json_match_data["data"]["attributes"]["mapName"],
            "duration": json_match_data["data"]["attributes"]["duration"],
            "gameMode": json_match_data["data"]["attributes"]["gameMode"]}


def collect_match_participant_stats(json_match_data: dict, participant_id: int) -> dict:
    '''
    collect stats for a player from a single match json data dict

    Args:
        json_match_data (dict): json data dict of a single match
        participant_id (int): participant id of the player

    Returns:
        dict: dict of player stats
    '''
    participant_stats = {}
    for entry in json_match_data["included"]:
        if entry["type"] == "participant":
            if entry["id"] == participant_id:
                participant_stats = entry["attributes"]["stats"]
                del participant_stats['name']
                del participant_stats['playerId']
                break
        if participant_stats:
            break
    return participant_stats


def collect_landing_location(json_telemetry: dict, player_name: str) -> dict:
    '''
    collect the landing location for a player from a single match telemetry data

    Args:
        json_telemetry (dict): json telemetry data dict for a single match
        player_name (str): player name

    Returns:
        dict: dict of landing location coordinates
    '''
    location_dict = {"landing_location_x": None, "landing_location_y": None, "landing_location_zone": None, "landing_time": None}
    for entry in json_telemetry:
        if "character" in entry and entry["character"]["name"] == player_name and entry["_T"] == "LogParachuteLanding":
            location_dict["landing_location_x"] = entry["character"]["location"]["x"]
            location_dict["landing_location_y"] = entry["character"]["location"]["y"]
            location_dict["landing_time"] = datetime.strptime(entry["_D"],"%Y-%m-%dT%H:%M:%S.%fZ")
            if entry["character"]["zone"]:
                location_dict["landing_location_zone"] = entry["character"]["zone"][0]
            break
    return location_dict


def collect_match_start_time(json_telemetry: dict) -> datetime:
    '''
    collect the start time of a match from telemetry data

    Args:
        json_telemetry (dict): json telemetry data dict for a single match

    Returns:
        datetime: start time of the match
    '''
    for entry in json_telemetry:
        if entry["_T"] == "LogMatchDefinition":
            start_time = datetime.strptime(entry["_D"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
            break
    return start_time


def collect_pick_drop_weapon_actions(json_telemetry: dict, player_name: str) -> list:
    '''
    collect the single player pick and drop actions for weapons from telemetry data

    Args:
        json_telemetry (dict): json telemetry data dict for a single match
        player_name (str): player name

    Returns:
        list: list of dicts with weapon, timepoint and action
    '''
    pick_drop_list = []

    start_time = collect_match_start_time(json_telemetry)

    for entry in json_telemetry:
        if "character" in entry and "item" in entry and entry["character"]["name"] == player_name and entry["item"][
            "category"] == "Weapon" and entry["item"]["subCategory"] == "Main" and entry["item"][
            "itemId"] != "Item_Weapon_vz61Skorpion_C" and entry["item"]["itemId"] != "Item_Weapon_FlareGun_C":
            if entry["_T"] == "LogItemPickup":
                timepoint = datetime.strptime(entry["_D"].split(".")[0], "%Y-%m-%dT%H:%M:%S") - start_time
                timepoint = timepoint.total_seconds()
                weapon = entry["item"]["itemId"]
                pick_drop_list.append({"weapon": weapon, "timepoint": timepoint, "action": "pick"})
            if entry["_T"] == "LogItemDrop":
                timepoint = datetime.strptime(entry["_D"].split(".")[0], "%Y-%m-%dT%H:%M:%S") - start_time
                timepoint = timepoint.total_seconds()
                weapon = entry["item"]["itemId"]
                pick_drop_list.append({"weapon": weapon, "timepoint": timepoint, "action": "drop"})
    return pick_drop_list


def collect_time_interval_weapon_equipped(json_telemetry: dict, player_name: str, start_interval: int = Config.start_interval,
                                          interval_iteration: int = Config.interval_iteration, end_interval: int = Config.end_interval) -> dict:
    '''
    collect the weapons equipped by a player at different time points

    Args:
        json_telemetry (dict): json telemetry data dict for a single match
        player_name (str): player name
        start_interval (int, optional): start time point in seconds. Defaults to Config.start_interval.
        interval_iteration (int, optional): time interval in seconds. Defaults to Config.interval_iteration.
        end_interval (int, optional): end time point in seconds. Defaults to Config.end_interval.

    Returns:
        dict: dict of weapons equipped at different time points
    '''
    pick_drop_list = collect_pick_drop_weapon_actions(json_telemetry, player_name)

    weapon_time_dict = {}

    weapon_inventar = [None, None]
    #used to keep track of how many pick/drop actions have been processed
    used_index = 0

    for seconds_interval in range(start_interval, end_interval, interval_iteration):
        #check if there are still pick/drop actions available
        if used_index != len(pick_drop_list) - 1:
            for index,entry in enumerate(pick_drop_list):
                if entry["timepoint"] < seconds_interval:
                    if entry["action"] == "pick":
                        if not weapon_inventar[0]:
                            weapon_inventar[0] = Config.item_meta_dict[entry["weapon"]]
                        elif weapon_inventar[0] and weapon_inventar[1] and "Panzerfaust" in weapon_inventar:
                            weapon_inventar[weapon_inventar.index("Panzerfaust")] = Config.item_meta_dict[entry["weapon"]]
                        else:
                            weapon_inventar[1] = Config.item_meta_dict[entry["weapon"]]
                    if entry["action"] == "drop":
                        if weapon_inventar[0] == Config.item_meta_dict[entry["weapon"]]:
                            weapon_inventar[0] = None
                        else:
                            weapon_inventar[1] = None
                    used_index = index

        weapon_time_dict[seconds_interval] = weapon_inventar[:]

    final_weapon_dict = {}
    for time_interval in weapon_time_dict:
        final_weapon_dict[f"Weapon_One_Min_{int(time_interval/60)}"] = weapon_time_dict[time_interval][0]
        final_weapon_dict[f"Weapon_Two_Min_{int(time_interval / 60)}"] = weapon_time_dict[time_interval][1]

    return final_weapon_dict