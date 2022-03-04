# @credit to : https://www.sqlitetutorial.net/sqlite-python/
import sqlite3, os, time, datetime
from sqlite3 import Error
from unittest import result

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file) # Establish a connection to the database
        # print(sqlite3.version)
        return conn
    except Error as e:
        print(e)
    #finally: Use just to connect and close
    #    if conn:
    #        conn.close()

    return conn

def create_std_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor() # cursor() allows Python to execute PostgreSQL command in a database session
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_df_tables(conn):
    """ create a table from the table variable
    :param conn: Connection object
    :return:
    Attention: result value is -1 to loss, 0 to tie and 1 to win
    """
    table_players = """ CREATE TABLE IF NOT EXISTS player (
                            id integer PRIMARY KEY AUTOINCREMENT,
                            name text NOT NULL
                        );"""

    table_gameMode = """ CREATE TABLE IF NOT EXISTS gameMode (
                            id integer PRIMARY KEY AUTOINCREMENT,
                            name text NOT NULL
                        );"""

    table_stats = """ CREATE TABLE IF NOT EXISTS stats (
                        id integer PRIMARY KEY AUTOINCREMENT,
                        result integer NOT NULL,
                        timeStamp text NOT NULL,
                        gameMode integer NOT NULL,
                        player_id integer NOT NULL,
                        FOREIGN KEY (gameMode) REFERENCES gameMode (id),
                        FOREIGN KEY (player_id) REFERENCES player (id)
                    );"""

    try:
        c = conn.cursor() # cursor() allows Python to execute PostgreSQL command in a database session
        c.execute(table_players)
        c.execute(table_gameMode)
        c.execute(table_stats)
    except Error as e:
        print(e)

def insert_gameMode(conn, name):
    """
    Create a new Game Mode
    :param conn: Connection object
    :param name: String containing the name od the mode
    :return: True if success
    """
    try:
        query = f" INSERT INTO gameMode(name) VALUES('{name}') ;"
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return True
    except Error as e:
        return e

def insert_player(conn, name):
    """
    Create a new player
    :param conn: Connection object
    :param name: String containing the name of the player
    :return: True if success
    """
    try:
        query = f" INSERT INTO player(name) VALUES('{name}') ;"
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return True
    except Error as e:
        return e

def insert_stats(conn, data):
    """
    Create a new game record
    :param conn: Connection object
    :param data: Dict containing the data to insert
    :return: True if success
    """
    formated_data = data[0]
    for i in range(1,len(data)):
        if type(data[i]) == str:
            formated_data = f"{formated_data}, '{data[i]}'"
        else:
            formated_data = f"{formated_data}, '{data[i]}'"
    try:
        query = f" INSERT INTO stats(result, timeStamp, gameMode, player_id) VALUES({formated_data}) ;"
        c = conn.cursor()
        c.execute(query)
        conn.commit()
        return True
    except Error as e:
        return e
    
def getData_fromDB(conn, table, fields, conditions):
    """
    Select fields from table
    :param conn: Connection object
    :param table: String containing the table name
    :param fields: dict containig the fileds to access
    :return: selected data
    """
    selectors = fields[0]
    for i in range(1,len(fields)):
        selectors = f'{selectors}, {selectors[i]}'
    try:
        if conditions == '':
            query = f" Select {selectors} from {table} ;"
        else: 
            query = f" Select {selectors} from {table} {conditions} ;"
        c = conn.cursor()
        c.execute(query)
        return c.fetchall()
    except Error as e:
        return e

def operation_test(conn):
    """
    Tests operations (insertions and selections) with the database
    :param conn: Connection object
    :return:
    """
    value = getData_fromDB(conn, 'player', ['id'], "WHERE name = 'goncalo' ")
    if value == []:
        insert_player(conn, 'goncalo')
        value = getData_fromDB(conn, 'player', ['id'], "WHERE name = 'goncalo' ")
    player_id = value[0][0]
    mode_id = getData_fromDB(conn, 'gameMode', ['id'], "WHERE name = 'solo' ")
    tS = datetime.datetime.now()
    print(insert_stats(conn, [1, str(tS) , mode_id, player_id]))


def prepare_db(conn):
    """
    Prepares de database with the gameMode values
    :param conn: Connection object
    :return: True if no errors, otherwise False
    """
    create_df_tables(conn)
    if getData_fromDB(conn, 'gameMode', ['*'], '') == []:
        success = []
        success.append(insert_gameMode(conn, 'solo'))
        success.append(insert_gameMode(conn, 'poly'))
        success.append(insert_gameMode(conn, 'lan'))
        for res in success:
            if res != True:
                print(res)
                return False
    return True
    
"""
-- Example table
CREATE TABLE IF NOT EXISTS tasks (
    id integer PRIMARY KEY,
    name text NOT NULL,
    priority integer,
    project_id integer NOT NULL,
    status_id integer NOT NULL,
    begin_date text NOT NULL,
	end_date text NOT NULL,
	FOREIGN KEY (project_id) REFERENCES projects (id)
);
"""
# os.remove("GameResults.db") DEBUG
# conn = create_connection("GameResults.db") DEBUG
# prepare_db(conn) DEBUG
# operation_test(conn) DEBUG    
