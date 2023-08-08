# PUBG-Data-Loader
Query the [pubg api](https://developer.pubg.com/) for matches of all tracked players that are listed in the Config.py file. Match and telemetry data are saved as individual json files, transformed and filtered with a separate python script and afterwards stored in a SQL database. SQL database gets than queried for final table overviews and plots.
