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

    def Read_Parquet_Data(self, path, table_name):
        """
        This function reads data from Parquet format databases stored in S3 buckets

        Parameters:
        ------------------------------------------------------------
        path: String
            It should be dictionary details of S3 bucket
        
        table_name: String
            Final table name of the Parquet dataset

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
        print(bucket_uri)
        try:
            dataset = pq.ParquetDataset(bucket_uri, filesystem=self.__fs).read().to_pandas()
            return dataset
        except Exception as Ex:
            print(f"Error reading Parquet table {table_name} : {Ex}")
        return None
