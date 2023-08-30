import sys
import json
import boto3
import pandas as pd
import snowflake.connector as snow
from datetime import datetime
from snowflake.connector.pandas_tools import write_pandas

class snowflake_connect:
    # !/usr/bin/env python
    # -*- coding: utf-8 -*-
    # Author: Devendra Kumar Sahu
    # Email: devsahu99@gmail.com
    # Sqliite DB related tasks
    """
    This is a support function to work with snowflake database from AWS Sagemaker. This function leverages secrets manager for retrietving the username, password and DB URL. It helps in quickly creating DB and interacting with the database by supporting functions.
    
    Parameters:
    ------------------------------------------------------------
    configs_data: dict, optional
        It should be dictionary contianing key details to connect with the Snowflake database. The expected keys are:
        warehouse: snowflake warehouse
        database: snowflake database
        schema: snowflake schema
        -----The below parameters are for secrets manager---------
        aws_region: region of AWS secrets manager
        secret_manager_urn: AWS secrets manager resource URL
        aws_secret_manager_name: name of secrets manager
        db_username_secret_key: the key name in secrets manager which stores username for snowflake
        db_password_secret_key: the key name in secrets manager which stores password for snowflake
        db_url_secret_key: the key name in secrets manager which stores url for snowflake
        
    db_table_dict_def: dict, optional
        definitions of database tables. This is reqquired when functionality of table creation is expected from this function
        
    ------------------------------------------------------------
    Returns:
    
    DataFrames with with provided SQL queries
    ------------------------------------------------------------
    Approach:

    1. Create an instance of SQL function
         mysql = snowflake_connect(configs_data, db_table_dict_def)

    2. Call table creation function
         mysql.Insert_To_Snowflake(df_to_insert, db_table)

    3. Insert values to the created table
        mysql.Get_Data_From_Snowflake(query)
        
    ------------------------------------------------------------    
    """
    def __init__(self, configs_data={}, db_table_dict_def={}):
        try:
            self.__region_name = configs_data['aws_region']
            self.__warehouse = configs_data['warehouse']
            self.__database = configs_data['database']
            self.__schema = configs_data['schema']
            secret_manager_urn = configs_data['secret_manager_urn']
            secret_manager_name = configs_data['aws_secret_manager_name']
            self.__db_username_key = configs_data['db_username_secret_key']
            self.__db_password_key = configs_data['db_password_secret_key']
            self.__db_url_key = configs_data['db_url_secret_key']
            self.__db_table_dict = db_table_dict_def
            secrets = boto3.client(service_name=secret_manager_name, region_name=self.__region_name)
            response = secrets.get_secret_value(SecretId=secret_manager_urn)
            self.__secrets = json.loads(response['SecretString'])
            self.__db_params = {}
        except Exception as ex:
            print(f"Issue in secrets DB parameter loading cannot proceed with DB parameter settings: {ex}")
        try:
            self.__db_params['db_user_name'] = self.__secrets.get(self.__db_username_key)
            self.__db_params['db_password'] = self.__secrets.get(self.__db_password_key)
            self.__db_params['db_url'] = self.__secrets.get(self.__db_url_key)
            self.__db_params['db_warehouse'] = self.__warehouse
            self.__db_params['db_database'] = self.__database
            self.__db_params['db_schema'] = self.__schema
        except Exception as ex:
            print(f"Issue in secrets DB parameter loading cannot proceed with DB parameter settings: {ex}")
    
    def Get_Secrets(self, prefix_env_secret_key=None):
        tdb_params = {}
        if prefix_env_secret_key:
            try:
                tdb_params['db_user_name'] = self.__secrets.get(f"{prefix_env_secret_key}_username")
                tdb_params['db_password'] = self.__secrets.get(f"{prefix_env_secret_key}_password")
                tdb_params['db_url'] = self.__secrets.get(f"{prefix_env_secret_key}_url")
                tdb_params['db_warehouse'] = self.__warehouse
                tdb_params['db_database'] = self.__database
                tdb_params['db_schema'] = self.__schema
                return tdb_params
            except Exception as ex:
                return f'Environment configuration not applicable: {ex}'
        return 'No Parameters'
    
    def __Get_DB_Params(self, d_params):
        db_params = self.__db_params
        if d_params:
            db_params = d_params
        return db_params
    
    def __Connect_To_Snowflake(self, d_params):
        print("Connecting to Snowflake")
        db_params = self.__Get_DB_Params(d_params)
        try:
            ctx = snow.connect(user=db_params['db_user_name'], password=db_params['db_password'], account=db_params['db_url'], warehouse=db_params['db_warehouse'], database=db_params['db_database'], schema=db_params['db_schema'])
            print("Connected to Snowflake")
            return ctx
        except Exception as ex:
            print(f"An Error Occured in Connecting to snowflake: {ex}")
        return None
    
    def Insert_To_Snowflake(self, df_to_insert, db_table, truncate=True, d_params=None, identifiers_flag=False, over_write_field=None):
        """
        This Function inserts the dataframe information into the snowflake table
        
        Parameters:
        ------------------------------------------------------------
        df_to_insert: Pandas dataframe
            dataframe to be inserted into snowflake database
            
        db_table: String
            Table name to which the data should be inserted
            
        truncate: Boolean, optional
            Default, True. If it is True then it will truncate the database table before inserting new data
        
        d_params: Dict, optional
            Default, None. It is required if configuration information is not provided during initial function call. The below mentioned keys should be provided in the dictionary format
                d_params['db_user_name'] = username to access the snowflake database
                d_params['db_password'] = password to access the snowflake database
                d_params['db_url'] = snowflake url
                d_params['db_warehouse'] = warehouse name
                d_params['db_database'] = database name
                d_params['db_schema'] = schema name
        
        identifiers_flag: Boolean, optional
            Default, False. If it is True then it will insert the data with identifiers into snowflake
            
        over_write_field: String, optional
            Default, None. Should be used when trunctate=False. A field name which will be used to overwrite the rows, wherever this keys information is available in already existing snowflake table those rows will be over will be deleted before inserting new data into the table
            
        ------------------------------------------------------------
        
        Returns:
        Success message
        
        Example:
        
        mysql.Insert_To_Snowflake(df, 'USERS')
        
        """
        try:
            print('Refresh Started')
            ctx = self.__Connect_To_Snowflake(d_params)
            cs = ctx.cursor()
            result = self.__checkDBTables(cs, db_table)
            if result:
                i = 1  # no action required, the table exists in the database
            else:
                print(f"Table doesn't exists, creating table {db_table}")
                ctx.cursor().execute(f"CREATE OR REPLACE TABLE {self.__db_table_dict[db_table]}")
            if over_write_field is not None:
                condition = f"""{over_write_field} in ({', '.join(["'"+str(x)+"'" for x in df_to_insert[over_write_field].unique()])})"""
                allrows = cs.execute(f"delete from {db_table} where {condition}").fetchall()
            if truncate:
                allrows=cs.execute(f""" truncate table {db_table} """).fetchall()

            if identifiers_flag:
                success, nchunks, nrows, _ = write_pandas(ctx, df_to_insert, db_table, quote_identifiers=True)
            else:
                success, nchunks, nrows, _ = write_pandas(ctx, df_to_insert, db_table, quote_identifiers=False)
            ctx.close()
            print(f'Refresh Sucessfull :: Success:{str(success)}; Chunks: {str(nchunks)}; Rows: {str(nrows)}')

        except Exception as ex:
            # sys.stdout = open("log.txt", "w")
            print(f"Unable to the write {db_table} to snowflake - exiting run")
            print(datetime.now().replace(microsecond=0), ex)
            sys.exit()
        return None
    
    def Get_Data_From_Snowflake(self, query, d_params=None):
        """
        This Function inserts the dataframe information into the snowflake table
        
        Parameters:
        ------------------------------------------------------------
        query: String
            SQL query to fetch the data
            
        d_params: Dict, optional
            Default, None. It is required if configuration information is not provided during initial function call. The below mentioned keys should be provided in the dictionary format
                d_params['db_user_name'] = username to access the snowflake database
                d_params['db_password'] = password to access the snowflake database
                d_params['db_url'] = snowflake url
                d_params['db_warehouse'] = warehouse name
                d_params['db_database'] = database name
                d_params['db_schema'] = schema name
        
        ------------------------------------------------------------
        Returns:
        Pandas dataframe
        
        Example:
        
        mysql.Get_Data_From_Snowflake(query)
        
        """
        try:
            ctx = self.__Connect_To_Snowflake(d_params)
            df = pd.read_sql_query(query, ctx)
            ctx.close()
            print("Data Fetch Completed")
            return df
        except:
            print(f"Data Fetching failed for the query: {query}")
            ctx.close()
        return None
    
    def __checkDBTables(self, cursor, tablename):
        stmt = "SHOW TABLES LIKE '%s' "% (str(tablename))
        cursor.execute(stmt)
        result = cursor.fetchone()
        return result

    def Fetch_All_Table_Names(self, d_params=None):
        """
        This Function returns the list of tables in the database schema
        
        Parameters:
        ------------------------------------------------------------
        d_params: Dict, optional
            Default, None. It is required if configuration information is not provided during initial function call. The below mentioned keys should be provided in the dictionary format
                d_params['db_user_name'] = username to access the snowflake database
                d_params['db_password'] = password to access the snowflake database
                d_params['db_url'] = snowflake url
                d_params['db_warehouse'] = warehouse name
                d_params['db_database'] = database name
                d_params['db_schema'] = schema name
        ------------------------------------------------------------
        
        Returns: String
        list of DB tables
        
        Example:
        
        mysql.getAllSFTablesList()
        
        """
        ctx = self.__Connect_To_Snowflake(d_params)
        all_tables = ctx.cursor().execute("show tables")
        ctx.close()
        return [x[1] for x in all_tables]

    def Drop_Tables_From_DB(self, tables_list, d_params=None):
        """
        This Function drops the mentioned tables from the snowflake database
        
        Parameters:
        ------------------------------------------------------------
        tables_list: List
            list of table names to be dropped
            
        d_params: Dict, optional
            Default, None. It is required if configuration information is not provided during initial function call. The below mentioned keys should be provided in the dictionary format
                d_params['db_user_name'] = username to access the snowflake database
                d_params['db_password'] = password to access the snowflake database
                d_params['db_url'] = snowflake url
                d_params['db_warehouse'] = warehouse name
                d_params['db_database'] = database name
                d_params['db_schema'] = schema name
        ------------------------------------------------------------
        
        Returns:
        Success messsage
        
        Example:
        
        mysql.dropSFTablesList(['USERS', 'ACCOUNTS', 'SALES'])
        
        """
        ctx = self.__Connect_To_Snowflake(d_params)
        if len(tables_list) > 0:
            for table in tables_list:
                try:
                    ctx.cursor().execute(f"drop table {table};")
                    print(f"Deleted : {table}")
                except:
                    print(f"Doesn't exist : {table}")
        ctx.close()
        return None
