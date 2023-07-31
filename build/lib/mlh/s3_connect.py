import io
from io import StringIO
import boto3
import pandas as pd
import sagemaker


class s3_connect:
    # !/usr/bin/env python
    # -*- coding: utf-8 -*-
    # Author: Devendra Kumar Sahu
    # Email: devsahu99@gmail.com
    # Sqliite DB related tasks
    """
    This is a support function to work with S3 bucket in AWS environment. This function is used to store retrieve files in different formats from the S3 bucket.
    
    Parameters:
    ------------------------------------------------------------
    configs_data: dict
        It should be dictionary containing key details to connect with S3 bucket. The expected keys are:
        s3Bucket: S3 bucket name
        kms: KMS key of the S3 bucket
        
    ------------------------------------------------------------
    Returns:
    
    Requested files from S3 bucket
    ------------------------------------------------------------
    Approach:

    1. Create an instance of SQL function
         my_s3 = s3_connect(configs_data)

    2. Call table creation function
         my_s3.Read_S3_File('my_ml_model.pkl')
        
    ------------------------------------------------------------    
    """
    def __init__(self, configs_data):
        self.__bucket = configs_data['s3Bucket']
        self.__kms = configs_data['kms']
        self.__s3 = boto3.client('s3')
    
    def Read_S3_File(self, file_name, filetype='obj', sheetname=None):
        """
        This is a support function to read S3 files.

        Parameters:
        ------------------------------------------------------------
        file_name: String
            name of the file in the S3 bucket. The name requires full path of the file
            
        filetype: String. Default: obj. Values: 'obj', 'excel', 'csv', 'text'
            Type of the files to be read from S3 bucket
            obj: if the file should be read as an object. e.g. pickle files, raw format files
            excel: if the file is in Excel format. Sheetname would be required in case of multiple sheets in the excel file
            csv: if the file type is csv file
            txt: if the file type is text file
        
        sheetname: applicable only for filetyp of 'excel'
            Name of the sheet in the excel file
        ------------------------------------------------------------
        Returns:

        Requested files from S3 bucket
        ------------------------------------------------------------
        Approach:

        1. Create an instance of SQL function
             my_s3 = s3_connect(configs_data)

        2. Call table creation function
             my_s3.Read_S3_File('my_excel_file.xlsx', filetype='excel', sheetname='my_second_sheet')

        ------------------------------------------------------------    
        """
        # filetype = ['obj', 'excel', 'csv', 'text']
        obj = self.__s3.get_object(Bucket=self.__bucket, Key=file_name)
        if filetype == 'obj':
            return obj['Body'].read()
        if filetype == 'excel':
            if sheetname:
                temp_df = pd.read_excel(io.BytesIO(obj['Body'].read()), sheet_name=sheetname)
                return temp_df.applymap(str)
            temp_df = pd.read_excel(io.BytesIO(obj['Body'].read()))
            return temp_df.applymap(str)
        if filetype == 'csv':
            temp_df = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='latin1')
            temp_df = temp_df.applymap(str)
            return temp_df
        if filetype == 'text':
            content = obj['Body'].read().decode('utf-8')
            return content
        print(f"Error: File type not found for {file_name}, while reading file from S3 Bucket")
        return None
    
    def Save_To_S3(self, df, file_name, excel=False):
        """
        Saving pandas dataframe to S3 bucket.

        Parameters:
        ------------------------------------------------------------
        df: Dataframe
            The pandas dataframe to be saved to S3
            
        file_name: String
            name of the file for the S3 bucket. The name requires full path of the file
            
        excel: Boolean. Default: False
            True, if the file should be saved as excel file
            False, the dataframe will be saved as csv file

        ------------------------------------------------------------
        Returns:
        Success message
        
        ------------------------------------------------------------
        Example:
         my_s3 = s3_connect(configs_data)
         
        1. Files saving
            my_s3.Save_To_S3(df, 'myfile.csv', excel=False)
            
            my_s3.Save_To_S3(df, 'myfile.xlsx', excel=True)
            
        2. Additional method to save multiple dataframes into excel sheets
        
            outputFile = "Output/myfile.xlsx"
             with io.BytesIO() as output:
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='mysheet', index=False)
                my_s3.Save_To_S3(output, outputFile, excel=True)

        ------------------------------------------------------------    
        """
        key = file_name
        if excel:
            data = df.getvalue()
            self.__s3.put_object(Body=data, Bucket=self.__bucket, Key=key, ServerSideEncryption='aws:kms', SSEKMSKeyId=self.__kms)
        else:
            csv_buffer = StringIO()
            df.to_csv(csv_buffer)
            self.__s3.put_object(Body=csv_buffer.getvalue(), Bucket=self.__bucket, Key=key, ServerSideEncryption='aws:kms', SSEKMSKeyId=self.__kms)
        return "Success"
    
    def Copy_To_S3(self, file_name, s3_folder_path):
        args = {'ServerSideEncryption':'aws:kms', 'SSEKMSKeyId':self.__kms}
        sagemaker.Session().upload_data(file_name, self.__bucket, s3_folder_path, extra_args=args)
        print("File Saved to S3")
        return None
