import sqlite3
from sqlite3 import Error
import pandas as pd

class sqlite_functions:
    # !/usr/bin/env python
    # -*- coding: utf-8 -*-
    # Author: Devendra Kumar Sahu
    # Email: devsahu99@gmail.com
    # Sqliite DB related tasks
    """
    This is a support function to work with local sqlite database. It helps in quickly creating DB and interacting with the database by supporting functions.
    
    Parameters:
    ------------------------------------------------------------
    db_path: int
        Existing local DB file path. If doesn't exists, then the function creates a new DB file.
    ------------------------------------------------------------
    Returns:
    
    DataFrames with with provided SQL queries
    ------------------------------------------------------------
    Approach:

    1. Create an instance of SQL function
         mysql = sqlite_functions(db_path)

    2. Call table creation function
         mysql.create_db_table(db_table_schema)

    3. Insert values to the created table
        mysql.insert_values_to_table(df, table_name)
    
    4. Extract saved data
        mysql.db_extract_records(query)
        
    ------------------------------------------------------------    
    """
    def __init__(self, db_path):
        self.__db_path = db_path
        
    def __connect_to_db(self):
        """
        Connect to an SQlite database, if db file does not exist it will be created
        :param db_file: absolute or relative path of db file
        :return: sqlite3 connection
        """
        sqlite3_conn = None
        try:
            sqlite3_conn = sqlite3.connect(self.__db_path)
            return sqlite3_conn
        except sqlite3.Error as err:
            print(f"Error in Connection: {err}")
            if sqlite3_conn is not None:
                sqlite3_conn.close()
        return None
    
    def create_db_table(self, tablemaps):
        """
        This Function creates database table.
        
        Parameters:
        ------------------------------------------------------------
        tablemaps: string
            Database table definition
        ------------------------------------------------------------
        Returns:
        An empty table is created in the database file
        
        Example:
        
        mysql = sqlite_functions(db_path)
        table_schema = 'users(USERID INTEGER, USER_NAME TXT, LAST_NAME TXT, ENTER_DATE REAL)'
        mysql.create_db_table(table_schema)
        """
        conn = self.__connect_to_db()
        if conn is not None:
            conn.execute("CREATE TABLE IF NOT EXISTS "  + tablemaps)
            print("Table Created")
            conn.close()
            return None
        print("Table Not Created!")
        conn.close()
        return None
    
    def drop_db_table(self, table_name):
        """
        This Function drops the created database table.
        
        Parameters:
        ------------------------------------------------------------
        table_name: string
            Database table name
        ------------------------------------------------------------
        Returns:
        None
        
        Example:
        
        mysql = sqlite_functions(db_path)
        mysql.drop_db_table('users')
        """
        conn = self.__connect_to_db()
        try:
            conn.execute("DROP TABLE "+ table_name)
            conn.close()
            print(f"{table_name} Deleted")
        except sqlite3.Error as err:
            conn.close()
            print(f"Can Not Delete {table_name} due to:- {err}")
        return None
    
    def db_delete_records(self, query, args=[]):
        """
        This Function delete certain records from the database table.
        
        Parameters:
        ------------------------------------------------------------
        query: string
            Database query string
        ------------------------------------------------------------
        Returns:
        None
        
        Example:
        
        query = 'DELETE FROM USERS where USERID>=5'
        mysql.db_delete_records(query)
        """
        conn = self.__connect_to_db()
        try:
            qury_result = conn.execute(query,args)
            conn.commit()
            conn.close()
            return None
        except sqlite3.Error as err:
            print(f"Cannot delete records for {query} due to:- {err}")
        return None
    
    def db_extract_records(self, query, args=[]):
        """
        This Function queries the database table and return the results into a pandas dataframe.
        
        Parameters:
        ------------------------------------------------------------
        query: string
            Database query string
        ------------------------------------------------------------
        Returns:
        Pandas dataframe
        
        Example:
        
        query = 'select * from USERS where USERID>=2'
        mysql.db_extract_records(query)
        """
        conn = self.__connect_to_db()
        try:
            qury_result = conn.execute(query,args)
            if str(qury_result.description)=='None':
                conn.close()
                return None
            names = [description[0] for description in qury_result.description]
            df = pd.DataFrame([x for x in qury_result],columns=names)
            conn.close()
            return df
        except sqlite3.Error as err:
            print(f"Cannot fetch records for {query} due to:- {err}")
        return None
    
    def __get_column_names_from_db_table(self, sql_cursor, table_name):
        table_column_names = 'PRAGMA table_info(' + table_name + ');'
        sql_cursor.execute(table_column_names)
        table_column_names = sql_cursor.fetchall()
        column_names = list()
        for name in table_column_names:
            column_names.append(name[1])
        return column_names
    
    def insert_values_to_table(self, df, table_name):
        """
        This Function inserts records to the database table.
        
        Parameters:
        ------------------------------------------------------------
        df: Pandas dataframe
            Pandas dataframe to be inserted into the database table
        table_name: String
            Table name to which the data should be inserted
        ------------------------------------------------------------
        
        Returns:
        None
        
        Example:
        mysql.insert_values_to_table(df, 'USERS')
        """
        conn = self.__connect_to_db()
        if conn is not None:
            cur = conn.cursor()

            db_columns = self.__get_column_names_from_db_table(cur, table_name)
            try:
                df[db_columns].to_sql(name=table_name, con=conn, if_exists='append', index=False)
                print('SQL insert process finished')
            except sqlite3.Error as err:
                print(f'Value Insersion Failed due to {err}')
            finally:
                conn.close()   
        else:
            print('Connection to database failed')
        return None
    
    def insert_unique_to_table(self, df, table_name):
        """
        This Function inserts unique records to the database table.
        
        Parameters:
        ------------------------------------------------------------
        df: Pandas dataframe
            Pandas dataframe to be inserted into the database table
        table_name: String
            Table name to which the data should be inserted
        ------------------------------------------------------------
        
        Returns:
        None
        
        Example:
        mysql.insert_unique_to_table(df, 'USERS')
        """
        conn = self.__connect_to_db()
        if conn is not None:
            cur = conn.cursor()
            db_columns = self.__get_column_names_from_db_table(cur, table_name)
            for i in range(len(df)):
                try:
                    df[db_columns].iloc[i:i+1].to_sql(name = table_name, con=conn, if_exists='append', index=False)
                except sqlite3.Error as err:
                    pass #or any other action
            conn.close()
        else:
            print('Connection to database failed')
        return None
    
    def killSqlCon(self):
        """
        This Function kills the sql connection.

        ------------------------------------------------------------
        """
        sqlite3_conn = None
        try:
            sqlite3_conn = sqlite3.connect(self.__db_path)
        except sqlite3.Error as err:
            print(err)
            if sqlite3_conn is not None:
                pass
        sqlite3_conn.close()
        return 'Connection Closed'

    def pandas_to_sql_query(self, df, tableName):
        """
        This Function converts the dataframe to sql queries schema for creating SQL table schema
        
        Parameters:
        ------------------------------------------------------------
        df: Pandas dataframe
            
        table_name: String
            Table name to which the data should be inserted
        ------------------------------------------------------------
        
        Returns:
        Querystring which can be used for creating data table schema
        
        Example:
        
        mysql.pandas_to_sql_query(df, 'USERS')
        
        """
        df_dict = df.dtypes.to_dict()
        dtypeDict = {'object':' TEXT','float64':' REAL'}
        clintop_data_keys = [x+dtypeDict[str(df_dict[x])] for x in df_dict.keys()]
        return f"""{tableName.strip()}({','.join(clintop_data_keys)})"""
