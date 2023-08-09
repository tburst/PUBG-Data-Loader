import json
import pandas as pd
from datetime import datetime
import plotly.express as px
from PIL import Image

# local imports
import Config


def create_meta_dict(df:pd.DataFrame) -> dict:
    '''
    creates a dictionary with meta info about the final results data set

    Args:
        df (pd.DataFrame): the final results data set transformed from the SQL data

    Returns:
        dict: a dict of meta info like last_updated and newest match included
    '''
    row_count = df.shape[0]
    match_count = len(df["match_id"].unique())
    now = datetime.now()
    dt_string = now.strftime("%d.%m.%Y %H:%M:%S")
    last_match_date = df.sort_values("createdAt", ascending=False).iloc[0]["createdAt"]
    last_match_date = datetime.strptime(last_match_date, '%Y-%m-%dT%H:%M:%SZ')
    last_match_date = last_match_date.strftime("%d.%m.%Y %H:%M:%S")

    meta_data = {"row_count": row_count,
                 "match_count": match_count,
                 "last_updated": dt_string,
                 "newest_match_included": last_match_date}

    return meta_data


def transform_df() -> pd.DataFrame:
    '''
    loads data from sql database and transforms it into a ready to analyse df

    Returns:
        pd.DataFrame: the final results data set transformed from the SQL data
    '''
    conn = Config.create_connection(Config.sql_path)
    pubg_df = pd.read_sql_query("SELECT * from participant", conn)
    pubg_df = pubg_df.drop(pubg_df[pubg_df.gameMode != "squad"].index)
    pubg_df["Win"] = [True if row["winPlace"] == 1 else False for index, row in pubg_df.iterrows()]
    pubg_df["Top10"] = [True if row["winPlace"] <= 10 else False for index, row in pubg_df.iterrows()]
    pubg_df = pubg_df.replace({"mapName": Config.map_dict})
    for player in Config.relevant_player_list:
        pubg_df[f"{player}_participated"] = [row == 1 for row in pubg_df[f"{player}_participated"]]
    pubg_df.insert(0,"Key", pubg_df.match_id.str.cat(pubg_df.player_name, sep='-'))
    return pubg_df


def plot_landing_winplace_maps(df) -> None:
    '''
    plots the starting locations for first place games on the different maps

    Args:
        df (pd.DataFrame): the final results data set transformed from the SQL data

    Returns:
        None: saves the plots as html files
    '''
    for map_name in df["mapName"].unique():
        fig = px.scatter(df[df["mapName"] == map_name].drop_duplicates(subset='match_id', keep="first"),
                         x="landing_location_x", y="landing_location_y",
                         color="winPlace", color_continuous_scale=px.colors.diverging.RdYlGn[::-1], opacity=0.7,
                         width=1500, height=1500)
        map_img = Image.open(r"assets\{}_Main_High_Res.png".format(map_name))
        fig.add_layout_image(
            dict(
                source=map_img,
                xref="x",
                yref="y",
                x=0,
                y=0,
                sizex= Config.map_size_dict[map_name],
                sizey= Config.map_size_dict[map_name],
                sizing="stretch",
                opacity=1,
                layer="below"
            ))
        fig.update_traces(marker=dict(size=14,
                                      line=dict(width=2,
                                                color='DarkSlateGrey')),
                          selector=dict(mode='markers'))
        fig.update_layout(template="plotly_white")
        fig.update_layout(yaxis_autorange="reversed")
        fig.update_layout(showlegend=False)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        fig.update(layout_coloraxis_showscale=False)
        fig.write_html(r"visualizations\{}_landing_locations.html".format(map_name))
        print(f"{map_name} landing locations done")


if __name__ == '__main__':
    # create csv file
    df = transform_df()
    df.to_csv(r"transformed_data\PUBG.csv", index=False, encoding="utf-8")
    print("CSV file done")

    # create meta file
    meta_data = create_meta_dict(df)
    with open("transformed_data\\meta_data.json", "w") as write_file:
        json.dump(meta_data, write_file)
    print("meta file done")

    # plot landing locations
    plot_landing_winplace_maps(df)