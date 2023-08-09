import sqlite3
from sqlite3 import Error

#local imports
import Config

def create_table(conn:sqlite3.connect, create_table_sql:str) -> None:
    '''
    create table in sql database with provided table query

    Args:
        conn (sqlite3.connect): the connection to the sql database
        create_table_sql (str): the query to create the table

    Returns:
        None: creates the table in the sql database
    '''
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


if __name__ == '__main__':
    database = Config.sql_path

    sql_create_participant_table = f"CREATE TABLE participant " \
                                   f"({','.join([f'{column_name} {Config.participant_columns[column_name]}' for column_name in Config.participant_columns])} " \
                                   f",PRIMARY KEY(match_id,player_id) ); "

    # create a database connection
    conn = Config.create_connection(database)

    # create tables
    if conn is not None:
        # create participant table
        create_table(conn, sql_create_participant_table)
    else:
        print("Error! cannot create the database connection.")
