import s3fs
import pyarrow.parquet as pq

class data_from_parquet:
    # !/usr/bin/env python
    # -*- coding: utf-8 -*-
    # Author: Devendra Kumar Sahu
    # Email: devsahu99@gmail.com
    # Sqliite DB related tasks
    """
    This is a support function to read data from Parquest format databases stored in S3 buckets. This function works with AWS sagemaker in AWS environment
    
    Parameters:
    ------------------------------------------------------------
    configs_data: dict
        It should be dictionary containing key details to connect with S3 bucket having the data into Parquet formats. The expected keys are:
        parquet_s3_bucket: S3 bucket name
        
    ------------------------------------------------------------
    Returns:
    Requested data as pandas dataframe
    
    ------------------------------------------------------------
    Approach:

    1. Create an instance of SQL function
         my_parquet = data_from_parquet(configs_data)

    2. Call table creation function
         my_parquet.Read_Parquet_Data('Parent_Directory/Child_Directory', 'Final_Table_Directory')
        
    ------------------------------------------------------------    
    """
    def __init__(self, configs_data):
        self.__parquet_s3_bucket = configs_data['parquet_s3_bucket']
        self.__fs = s3fs.S3FileSystem()
        self.__name = 'data_from_parquet'

    def Read_Parquet_Data(self, path, table_name, cols=None, legacy_dataset=False):
        """
        This function reads data from Parquet format databases stored in S3 buckets

        Parameters:
        ------------------------------------------------------------
        path: String
            It should be dictionary details of S3 bucket
        
        table_name: String
            Final table name of the Parquet dataset
        
        cols: List
            List of columns to be selected

        ------------------------------------------------------------
        Returns:
            Pandas dataframe

        ------------------------------------------------------------
        Approach:

        1. Create an instance of SQL function
             my_parquet = data_from_parquet(configs_data)

        2. Call table creation function
             my_parquet.Read_Parquet_Data('Parent_Directory/Child_Directory', 'Final_Table_Directory')

        ------------------------------------------------------------    
        """
        print(f"Reading parquet data: {table_name}")
        bucket_uri = f"s3://{self.__parquet_s3_bucket}/{path}/{table_name}"
        paths = [path for path in fs.ls(bucket_uri) if path.endswith(".parquet")]
        print(bucket_uri)
        try:
            pds = pq.ParquetDataset(paths, filesystem=self.__fs, use_legacy_dataset=legacy_dataset)
            dataset = pds.read(columns=cols).to_pandas()
            return dataset
        except Exception as Ex:
            print(f"Error reading Parquet table {table_name} : {Ex}")
        return None
    
    def Get_Parquet_Data(self, path_key, cols=None, filters=None, legacy_dataset=False, top_rows=False):
        """
        This function reads data from Parquet format databases stored in S3 buckets

        Parameters:
        ------------------------------------------------------------
        path_key: String
            Fully qualified path and table name of the Parquet dataset
        
        cols: List
            List of columns to be selected
        
        filters: List, Touple
            List of filter conditions in the form of touples
            
        top_rows: Binary
            Whether to return the results from the first available parition
        ------------------------------------------------------------
        Returns:
            Pandas dataframe

        ------------------------------------------------------------
        Approach:

        1. Create an instance of SQL function
             my_parquet = data_from_parquet(configs_data)

        2. Call table creation function
             my_parquet.Get_Parquet_Data('Parent_Directory/Child_Directory/Final_Table_Directory')

        ------------------------------------------------------------    
        """
        print(f"Reading parquet data: {path_key.split('/')[-1]}")
        bucket_uri = f"s3://{self.__parquet_s3_bucket}/{path_key}"
        paths = [path for path in fs.ls(bucket_uri) if path.endswith(".parquet")]
        print(bucket_uri)
        try:
            if top_rows:
                pds = pq.ParquetDataset(paths[0], filesystem=self.__fs, filters=filters, use_legacy_dataset=legacy_dataset)
                dataset = pds.read_pandas(columns=cols).to_pandas()
                return dataset
            pds = pq.ParquetDataset(paths, filesystem=self.__fs, filters=filters, use_legacy_dataset=legacy_dataset)
            dataset = pds.read_pandas(columns=cols).to_pandas()
            return dataset
        except Exception as Ex:
            print(f"Error reading Parquet table {path_key.split('/')[-1]} : {Ex}")
        return None

    def Get_Parquet_Tables(self, path_key):
        """
        This function reads metadata from Parquet database path stored in S3 buckets

        Parameters:
        ------------------------------------------------------------
        path_key: String
            Fully qualified path and table name of the Parquet dataset

        ------------------------------------------------------------
        Returns:
            List of table names under the path

        ------------------------------------------------------------
        Approach:

        1. Create an instance of SQL function
             my_parquet = data_from_parquet(configs_data)

        2. Call table creation function
             my_parquet.Get_Parquet_Tables('Parent_Directory/Child_Directory')

        ------------------------------------------------------------    
        """
        try:
            key = f"{self.__parquet_s3_bucket}/{path_key}"
            path_list = fs.ls(f"s3://{key}")
            path_tables = [x.replace(f"{key}/", "") for x in path_list]
            path_tables = [x for x in path_tables if len(x) > 1]
            return path_tables
        except Exception as Ex:
            print(f"Error in reading the paths : {Ex}")
        return None

    def Get_Parquet_Schema(self, path_key, dtype=False):
        """
        This function reads the schema of the database table and return the name of the columns

        Parameters:
        ------------------------------------------------------------
        path_key: String
            Fully qualified path and table name of the Parquet dataset
        
        dtype: Binary
            If true returns the column names along with data types of the columns

        ------------------------------------------------------------
        Returns:
            List values

        ------------------------------------------------------------
        Approach:

        1. Create an instance of SQL function
             my_parquet = data_from_parquet(configs_data)

        2. Call table creation function
             my_parquet.Get_Parquet_Schema('Parent_Directory/Child_Directory/Final_Table_Directory')

        ------------------------------------------------------------    
        """
        bucket_uri = f"s3://{self.__parquet_s3_bucket}/{path_key}"
        paths = [path for path in fs.ls(bucket_uri) if path.endswith(".parquet")]
        print(bucket_uri)
        try:
            pq_schema = pq.ParquetDataset(paths, filesystem=self.__fs, use_legacy_dataset=False).schema
            if dtype:
                return pq_schema
            else:
                return pq_schema.names
        except Exception as Ex:
            print(f"Error reading Parquet schema for {table_name} : {Ex}")
        return None
