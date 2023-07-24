from datetime import datetime

#local imports
import Config

def identify_relevant_participants(account_id_dict, json_match_data):
    participant_id_dict = {}
    for entry in json_match_data["included"]:
        if entry["type"] == "participant":
            for player in account_id_dict:
                if entry["attributes"]["stats"]["playerId"] == account_id_dict[player]:
                    participant_id_dict[player] = entry["id"]
    return participant_id_dict


def collect_match_meta_data(json_match_data):
    return {"createdAt": json_match_data["data"]["attributes"]["createdAt"],
            "mapName": json_match_data["data"]["attributes"]["mapName"],
            "duration": json_match_data["data"]["attributes"]["duration"],
            "gameMode": json_match_data["data"]["attributes"]["gameMode"]}


def collect_match_participant_stats(json_match_data,participant_id):
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


def collect_landing_location(json_telemetry,player_name):
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


def collect_match_start_time(json_telemetry):
    for entry in json_telemetry:
        if entry["_T"] == "LogMatchDefinition":
            start_time = datetime.strptime(entry["_D"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
            break
    return start_time


def collect_pick_drop_weapon_actions(json_telemetry,player_name):
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


def collect_time_interval_weapon_equipped(json_telemetry,player_name,start_interval=Config.start_interval,interval_iteration=Config.interval_iteration, end_interval=Config.end_interval):
    pick_drop_list = collect_pick_drop_weapon_actions(json_telemetry, player_name)

    weapon_time_dict = {}

    weapon_inventar = [None, None]
    used_index = 0

    for seconds_interval in range(start_interval, end_interval, interval_iteration):
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