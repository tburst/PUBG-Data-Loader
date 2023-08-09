# PUBG-Data-Loader
Query the pubg api for matches of all tracked players that are listed in the Config.py file. Match and telemetry data are saved as individual json files, transformed and filtered with a separate python script and afterwards stored in a SQL database. SQL database gets then queried for final table overviews and plots.

## Project Structure

The project is divided into six main scripts:

1. **Config.py**: Configuration file containing the information of tracked players and other necessary settings.
2. **Setup_SQL.py**: Setting up the SQL database.
3. **Query_Api.py**: Fetches match and telemetry data from the PUBG API for the players listed in `Config.py`. The data is saved as individual JSON files.
4. **Transform_Raw_Data.py**: Contains functions to transform and filter the data from the raw JSON files. Functions are imported and used during the SQL storing in the next step.
5. **Store_SQL.py**: Takes and transformes the data and stores it into a SQL database.
6. **Create_Final_Results_Files.py**: Queries the SQL database for final table overviews and plots.

## Usage

Follow these steps to run the project:

1. **Configuration**:
   Edit `Config.py` to add the information of the players you want to track.

2. **Setup SQL**:
   Run `Setup_SQL.py` to setup the SQL database

3. **Query API**:
   Run `Query_Api.py` to fetch the raw match and telemetry data.

4. **Store Data in SQL**
   Run `Store_SQL.py` to transform match and telemetry data and store it in the SQL database.

5. **Create Output Files**
   Run `Create_Final_Results_Files.py` to create a data final ready-to-analyse table/dataset and landing location plots.

