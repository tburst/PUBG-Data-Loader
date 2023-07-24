from sqlite3 import Error

#local imports
import Config

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)



def main():
    database = Config.sql_path

    sql_create_participant_table = f"CREATE TABLE participant " \
                                   f"({','.join([f'{column_name} {Config.participant_columns[column_name]}'for column_name in Config.participant_columns])} " \
                                   f",PRIMARY KEY(match_id,player_id) ); "


    # create a database connection
    conn = Config.create_connection(database)

    # create tables
    if conn is not None:
        # create participant table
        create_table(conn, sql_create_participant_table)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
