import requests
import json
import os

#local imports
import Config

with open("api_key.txt", "r") as read_file:
    api_key = read_file.read()

main_url = "https://api.pubg.com/shards/steam"

header = {
  "Authorization": f"Bearer {api_key}",
  "Accept": "application/vnd.api+json"
}


def get_account_id_of_playernames(list_playernames:list):
    get_url = "/players"
    list_playernames = ",".join(list_playernames)
    r = requests.get(main_url + get_url, headers=header,
                     params={"filter[playerNames]": list_playernames})
    match_data = json.loads(r.content)
    player_id_dict = {entry["attributes"]["name"]: entry["id"] for entry in match_data["data"]}
    return player_id_dict


def get_matchlist_of_playernames(list_playernames:list):
    get_url = "/players"
    list_playernames = ",".join(list_playernames)
    r = requests.get(main_url + get_url, headers=header,
                     params={"filter[playerNames]": list_playernames})
    match_data = json.loads(r.content)
    match_dict = {}
    for entry in match_data["data"]:
        player_name = entry["attributes"]["name"]
        match_dict[player_name] = [match["id"] for match in entry["relationships"]["matches"]["data"]]
    return match_dict


def save_match_data(list_playernames:list):
    file_list = os.listdir("raw_data\\matches")
    get_url = "/matches"
    match_dict = get_matchlist_of_playernames(list_playernames)
    unique_match_id_list = set([match_id for playername in match_dict for match_id in match_dict[playername]])
    for match_id in unique_match_id_list:
        if f"{match_id}.txt" not in file_list:
            r = requests.get(main_url + get_url + f"/{match_id}", headers=header)
            match_json = json.loads(r.content)
            with open(f'raw_data\\matches\\{match_id}.txt', 'w') as outfile:
                json.dump(match_json, outfile)
            print(f"{match_id}.txt file added")

def identify_telemetry_url(match_data_json):
    tele_id = match_data_json["data"]["relationships"]["assets"]["data"][0]["id"]
    for entry in match_data_json["included"]:
        if "id" in entry:
            if entry["id"] == tele_id:
                return entry["attributes"]["URL"]


def save_telemetry_data():
    match_file_list = os.listdir("raw_data\\matches")
    tele_file_list = os.listdir("raw_data\\telemetry")
    query_list = [match_id for match_id in match_file_list if match_id not in tele_file_list]
    for match_id in query_list:
        with open(f"raw_data\\matches\\{match_id}", "r") as read_file:
            match_data_json = json.load(read_file)
        tele_url = identify_telemetry_url(match_data_json)
        r = requests.get(tele_url , headers=header)
        tele_json = json.loads(r.content)
        with open(f'raw_data\\telemetry\\{match_id}', 'w') as outfile:
            json.dump(tele_json, outfile)
        print(f"{match_id}.txt telemetry data file added")


if __name__ == "__main__":
    save_match_data(Config.relevant_player_list)
    save_telemetry_data()