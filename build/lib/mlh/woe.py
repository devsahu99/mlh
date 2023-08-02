import pandas as pd
import pandas.core.algorithms as algos
import scipy.stats.stats as stats
from pandas import Series
import numpy as np
import random
from IPython.display import display, HTML, Markdown
import matplotlib.pyplot as plt

class woe:
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # Author: Devendra Kumar Sahu
    # Email: devsahu99@gmail.com
    """
    This function will help to calculate Weight of Evidence and Information Value, the charts can be displayed and coarse classing can also be done using Reset_Woe() function.

    Parameters:
    ------------------------------------------------------------
    max_bin: int
        Maximum number of bins for numeric variables. The default is 10
    iv_threshold: float
        Threshold value for Information Value. Variables with higher than threshold will be considered for transformation
    ignore_threshold: Boolean
        This parameter controls whether the defined threshold should be considered or ignored. The default is 'True'
    ------------------------------------------------------------
    Returns:
    
    DataFrame having weight of evidence of each column along with the target variable
    ------------------------------------------------------------
    Approach:

    1. Create an instance of woe
         my_woe = woe()

    2. Call fit method on the defined object by passing on dataframe and the target variable name
         my_woe.fit(df,target)

    3. Call the transform method
        transformed_df = my_woe.transform()
        
    ------------------------------------------------------------
    # Example
    
    ### Create Sample DataFrame
    seed=1456
    np.random.seed(seed)
    random.seed(seed)
    
    rows = 1000
    
    y = random.choices([0,1],k=rows,weights=[.7,.3])
    
    x1 = random.choices(np.arange(20,40),k=rows)
    x2 = np.random.randint(1000,2000,size=rows)
    x3 = random.choices(np.arange(1,100),k=rows)
    x4 = random.choices(['m','f','u'],k=rows)
    x5 = random.choices(['a','b','c','d','e','f','g','h'],k=rows)
    
    df = pd.DataFrame({'y':y,'x1':x1,'x2':x2,'x3':x3,'x4':x4,'x5':x5})
    
    df.head()
    
    ### Create Instance of Weight of Evidence Package
    my_woe = woe()
    
    ### Fit the data with created instance
    my_woe.fit(df,'y')
    
    ### Display the relevant charts
    my_woe.Display_WOE_Charts()
    
    ### Get Information Value
    my_woe.Get_Information_Values()
    
    ### Replace the original values in the Dataframe with Weight of Evidence
    transformed_df = my_woe.transform()
    """
    def __init__(self,max_bin=10,iv_threshold=0.02,ignore_threshold=True):
        self.__max_bin = max_bin
        self.__force_bin = 2
        self.__threshold = iv_threshold
        self.__threshold_ignore = ignore_threshold
    # define a binning function
    def __mono_bin(self,X):
        n = self.__max_bin
        df1 = pd.DataFrame({"X": X, "Y": self.__target})
        justmiss = df1[['X','Y']][df1.X.isnull()]
        notmiss = df1[['X','Y']][df1.X.notnull()]
        r = 0
        while np.abs(r) < .95:
            try:
                d1 = pd.DataFrame({"X": notmiss.X, "Y": notmiss.Y, "Bucket": pd.qcut(notmiss.X, n)})
                d2 = d1.groupby('Bucket', as_index=True)
                r, p = stats.spearmanr(d2.mean().X, d2.mean().Y)
                n = n - 1
            except Exception as e:
                n = n - 1
        if len(d2) == 1:
            n = self.__force_bin
            bins = algos.quantile(notmiss.X, np.linspace(0, 1, n))
            if len(np.unique(bins)) == 2:
                bins = np.insert(bins, 0, 1)
                bins[1] = bins[1]-(bins[1]/2)
            d1 = pd.DataFrame({"X": notmiss.X, "Y": notmiss.Y, "Bucket": pd.cut(notmiss.X, np.unique(bins),include_lowest=True)})
            d2 = d1.groupby('Bucket', as_index=True)
        d3 = pd.DataFrame({},index=[])
        d3["MIN_VALUE"] = d2.min().X
        d3["MAX_VALUE"] = d2.max().X
        d3["COUNT"] = d2.count().Y
        d3["EVENT"] = d2.sum().Y
        d3["NONEVENT"] = d2.count().Y - d2.sum().Y
        d3=d3.reset_index(drop=True)
        if len(justmiss.index) > 0:
            d4 = pd.DataFrame({'MIN_VALUE':np.nan},index=[0])
            d4["MAX_VALUE"] = np.nan
            d4["COUNT"] = justmiss.count().Y
            d4["EVENT"] = justmiss.sum().Y
            d4["NONEVENT"] = justmiss.count().Y - justmiss.sum().Y
            d3 = d3.append(d4,ignore_index=True,sort=True)
        d3["EVENT_RATE"] = d3.EVENT/d3.COUNT
        d3["NON_EVENT_RATE"] = d3.NONEVENT/d3.COUNT
        d3["DIST_EVENT"] = d3.EVENT/d3.sum().EVENT
        d3["DIST_NON_EVENT"] = d3.NONEVENT/d3.sum().NONEVENT
        d3["WOE"] = np.log(d3.DIST_EVENT/d3.DIST_NON_EVENT)
        d3["IV"] = (d3.DIST_EVENT-d3.DIST_NON_EVENT)*np.log(d3.DIST_EVENT/d3.DIST_NON_EVENT)
        d3["VAR_NAME"] = "VAR"
        d3 = d3[['VAR_NAME','MIN_VALUE', 'MAX_VALUE', 'COUNT', 'EVENT', 'EVENT_RATE', 'NONEVENT', 'NON_EVENT_RATE', 'DIST_EVENT','DIST_NON_EVENT','WOE', 'IV']]
        d3['Iter'] = 1
        d3 = d3.replace([np.inf, -np.inf], 0)
        d3.IV = d3.IV.sum()
        return(d3)

    def __num_bin(self,X):
        n = self.__max_bin
        df1 = pd.DataFrame({"X": X, "Y": self.__target})
        justmiss = df1[['X','Y']][df1.X.isnull()]
        notmiss = df1[['X','Y']][df1.X.notnull()]
        r = 0
        while np.abs(r) < .5:
            try:
                d1 = pd.DataFrame({"X": notmiss.X, "Y": notmiss.Y, "Bucket": pd.qcut(notmiss.X, n)})
                d2 = d1.groupby('Bucket', as_index=True)
                r, p = stats.spearmanr(d2.mean().X, d2.mean().Y)
                n = n - 1
            except Exception as e:
                n = n - 1
        if len(d2) == 1:
            n = self.__force_bin
            bins = algos.quantile(notmiss.X, np.linspace(0, 1, n))
            if len(np.unique(bins)) == 2:
                bins = np.insert(bins, 0, 1)
                bins[1] = bins[1]-(bins[1]/2)
            d1 = pd.DataFrame({"X": notmiss.X, "Y": notmiss.Y, "Bucket": pd.cut(notmiss.X, np.unique(bins),include_lowest=True)})
            d2 = d1.groupby('Bucket', as_index=True)
        d3 = pd.DataFrame({},index=[])
        d3["MIN_VALUE"] = d2.min().X
        d3["MAX_VALUE"] = d2.max().X
        d3["COUNT"] = d2.count().Y
        d3["EVENT"] = d2.sum().Y
        d3["NONEVENT"] = d2.count().Y - d2.sum().Y
        d3=d3.reset_index(drop=True)
        if len(justmiss.index) > 0:
            d4 = pd.DataFrame({'MIN_VALUE':np.nan},index=[0])
            d4["MAX_VALUE"] = np.nan
            d4["COUNT"] = justmiss.count().Y
            d4["EVENT"] = justmiss.sum().Y
            d4["NONEVENT"] = justmiss.count().Y - justmiss.sum().Y
            d3 = d3.append(d4,ignore_index=True,sort=True)
        d3["EVENT_RATE"] = d3.EVENT/d3.COUNT
        d3["NON_EVENT_RATE"] = d3.NONEVENT/d3.COUNT
        d3["DIST_EVENT"] = d3.EVENT/d3.sum().EVENT
        d3["DIST_NON_EVENT"] = d3.NONEVENT/d3.sum().NONEVENT
        d3["WOE"] = np.log(d3.DIST_EVENT/d3.DIST_NON_EVENT)
        d3["IV"] = (d3.DIST_EVENT-d3.DIST_NON_EVENT)*np.log(d3.DIST_EVENT/d3.DIST_NON_EVENT)
        d3["VAR_NAME"] = "VAR"
        d3 = d3[['VAR_NAME','MIN_VALUE', 'MAX_VALUE', 'COUNT', 'EVENT', 'EVENT_RATE', 'NONEVENT', 'NON_EVENT_RATE', 'DIST_EVENT','DIST_NON_EVENT','WOE', 'IV']]
        d3['Iter'] = 0
        d3 = d3.replace([np.inf, -np.inf], 0)
        d3.IV = d3.IV.sum()
        return(d3)

    def __char_bin(self,X):
        df1 = pd.DataFrame({"X": X, "Y": self.__target})
        justmiss = df1[['X','Y']][df1.X.isnull()]
        notmiss = df1[['X','Y']][df1.X.notnull()]
        df2 = notmiss.groupby('X',as_index=True)
        d3 = pd.DataFrame({},index=[])
        d3["COUNT"] = df2.count().Y
        d3["MIN_VALUE"] = df2.sum().Y.index
        d3["MAX_VALUE"] = d3["MIN_VALUE"]
        d3["EVENT"] = df2.sum().Y
        d3["NONEVENT"] = df2.count().Y - df2.sum().Y
        if len(justmiss.index) > 0:
            d4 = pd.DataFrame({'MIN_VALUE':np.nan},index=[0])
            d4["MAX_VALUE"] = np.nan
            d4["COUNT"] = justmiss.count().Y
            d4["EVENT"] = justmiss.sum().Y
            d4["NONEVENT"] = justmiss.count().Y - justmiss.sum().Y
            d3 = d3.append(d4,ignore_index=True,sort=True)
        d3["EVENT_RATE"] = d3.EVENT/d3.COUNT
        d3["NON_EVENT_RATE"] = d3.NONEVENT/d3.COUNT
        d3["DIST_EVENT"] = d3.EVENT/d3.sum().EVENT
        d3["DIST_NON_EVENT"] = d3.NONEVENT/d3.sum().NONEVENT
        d3["WOE"] = np.log(d3.DIST_EVENT/d3.DIST_NON_EVENT)
        d3["IV"] = (d3.DIST_EVENT-d3.DIST_NON_EVENT)*np.log(d3.DIST_EVENT/d3.DIST_NON_EVENT)
        d3["VAR_NAME"] = "VAR"
        d3 = d3[['VAR_NAME','MIN_VALUE', 'MAX_VALUE', 'COUNT', 'EVENT', 'EVENT_RATE', 'NONEVENT', 'NON_EVENT_RATE', 'DIST_EVENT','DIST_NON_EVENT','WOE', 'IV']]
        d3['Iter'] = 0
        d3 = d3.replace([np.inf, -np.inf], 0)
        d3.IV = d3.IV.sum()
        d3 = d3.reset_index(drop=True)
        return(d3)

    def fit(self,df, target):
        """
        This Function fits the dataframe into weight of evidence matrix.
        
        Parameters:
        ------------------------------------------------------------
        df: Pandas DataFrame
            The dataframe to be fitted into weight of evidence matrix
        target: string
            The name of target (dependent) variable. The variable should be present in the dataframe passed in 'df'
        ------------------------------------------------------------
        
        Returns:
        DataFrame having weight of evidence of each column along with the target variable
        """
        self.__df = df
        self.__pred_var = target
        self.__target = df[target]
        self.__data_vars()
    def __data_vars(self):
        x = self.__df.dtypes.index
        count = -1
        for i in x:
            if i != self.__pred_var:
                if np.issubdtype(self.__df[i], np.number) and len(Series.unique(self.__df[i])) > 2:
                    conv_post = self.__mono_bin(self.__df[i])
                    conv_post["VAR_NAME"] = i
                    conv_pre = self.__num_bin(self.__df[i])
                    conv_pre["VAR_NAME"] = i
                    conv = pd.concat([conv_post,conv_pre])
                    count = count + 1
                else:
                    conv = self.__char_bin(self.__df[i])
                    conv["VAR_NAME"] = i
                    count = count + 1
                if count == 0:
                    iv_df = conv
                else:
                    iv_df = iv_df.append(conv,ignore_index=True,sort=True)
        self.__all_iv_df = iv_df
        iv = self.Get_Information_Values()
        self.__all_iv = iv
        if self.__threshold_ignore:
            self.__rel_iv = iv.reset_index(drop = True)
        else:
            self.__rel_iv = iv[iv['IV']>self.__threshold].reset_index(drop = True)
        self.__rel_iv_vars = [i for i in self.__rel_iv['VAR_NAME']]  
    def transform(self,relevant_variable_sublist='All'):
        """
        This Function transforms the originally fitted dataframe, it replaces original
        values with respective weight of evidence and removes the original columns.
        
        Parameters:
        ------------------------------------------------------------
        relevant_variable_sublist: String
            The default is 'All'. The list of relevant variables to be transformed
            
        ------------------------------------------------------------
        
        Returns:
        ------------------------------------------------------------
        Transformed DataFrame
        
        """
        max_rel_var = self.__all_iv_df.groupby(['VAR_NAME'])[['Iter']].agg('max').reset_index()
        self.__final_woe = pd.merge(max_rel_var,self.__all_iv_df,how='left',on=['VAR_NAME','Iter'])
        if relevant_variable_sublist=='All':
            final_rel_vars = self.__rel_iv_vars
        else:
            final_rel_vars = relevant_variable_sublist
        rel_var_dict = {key:value for (key,value) in zip(final_rel_vars,[i+'_woe' for i in final_rel_vars])}
        transf_df = self.__df[list(set(list(final_rel_vars+[self.__pred_var])))].copy()
        for i in range(len(final_rel_vars)):
            transf_df[rel_var_dict[final_rel_vars[i]]] = self.__replace_col(transf_df[final_rel_vars[i]],final_rel_vars[i])
        transf_df.drop(final_rel_vars,axis=1,inplace=True)
        return transf_df
    def Get_WOE_Values(self):
        """
        This Function returns the Information Values, Weight of Evidence and other details as a DataFrame
        
        """
        woe_max_iter = self.__all_iv_df.groupby(['VAR_NAME'])[['Iter']].agg('max').reset_index()
        latest_woe = pd.merge(self.__all_iv_df,woe_max_iter,on=['VAR_NAME','Iter'])
        return latest_woe
    def Set_Variable_Selection_Threshold(self, iv_threshold=0.02, ignore_threshold=False):
        """
        This Function sets the variable selection thresholds. The variables having Information Value higher 
        than this threshold are selected. 
        
        Parameters:
        ------------------------------------------------------------
        iv_threshold: float
            The default is 0.02. The maximum value can be .99
            
        ignore_threshold: Boolean
            This parameter controls whether the defined threshold should be considered or ignored. The default is 'False'
        ------------------------------------------------------------
        """
        iv = self.__all_iv
        if ignore_threshold:
            self.__rel_iv = iv.reset_index(drop = True)
        else:
            self.__rel_iv = iv[iv['IV']>self.__threshold].reset_index(drop = True)
        self.__rel_iv_vars = [i for i in self.__rel_iv['VAR_NAME']]
        return None
    def Get_Information_Values(self):
        """
        This Function returns latest iteration Information Values as a pandas DataFrame. 
        
        """
        woe_max_iter = self.__all_iv_df.groupby(['VAR_NAME'])[['Iter']].agg('max').reset_index()
        latest_woe = pd.merge(self.__all_iv_df,woe_max_iter,on=['VAR_NAME','Iter'])
        latest_iv = latest_woe.groupby(['VAR_NAME'])[['IV']].agg('max').reset_index()
        return latest_iv
    def Reset_Woe(self,variable_index = 0,reset_indexes=(0,1),previous_iteration=0):
        """
        This Function resets the weight of evidence of adjancent values where the chart is not smooth.
        The smoothness can be observed using the Display_WOE_Charts() function.
        
        Parameters:
        ------------------------------------------------------------
        variable_index: int
            The index of the variable displayed in the title of the charts. This index is maintained internally
            therefore, it is highly recommended to use the chart index only while using this reset function.
            
        reset_indexes: Tuple
            This parameter should a tuple indicating the adjacent indices on the chart to be combined. 
            The default is (0,1) which should be run only when the chart is not smooth between first and
            second index.
        
        previous_iteration: int
            This is the previous iteration number for calculated weight of evidence
        ------------------------------------------------------------
        """
        colname = self.__rel_iv_vars[variable_index]
        tups = reset_indexes
        iter_prev = previous_iteration
        iter_new = iter_prev+1
        # Delete the recently chaned iteration
        self.__all_iv_df.reset_index(drop = True,inplace = True)
        self.__all_iv_df.drop(self.__all_iv_df[(self.__all_iv_df.VAR_NAME==colname)&(self.__all_iv_df.Iter == iter_new)].index,axis = 0, inplace = True)
        # Create a temporary dataframe
        df = self.__all_iv_df[(self.__all_iv_df['VAR_NAME'] == colname) & (self.__all_iv_df['Iter'] == iter_prev)]
        df.reset_index(inplace = True)
        colvars = ['VAR_NAME','MIN_VALUE','MAX_VALUE','COUNT','EVENT','NONEVENT']
        rows = list(set(list(range(0,df.shape[0])))-set(tups))
        base = df[colvars].iloc[rows]
        aps = df[colvars].iloc[list(tups)]
        #Start Calculations
        min_value = aps['MIN_VALUE'].iloc[0]
        max_value = aps['MAX_VALUE'].iloc[1]
        min_aps = aps.groupby(['VAR_NAME'])[['COUNT','EVENT','NONEVENT']].agg('sum')
        min_aps['MIN_VALUE'] = min_value
        min_aps['MAX_VALUE'] = max_value
        min_aps.reset_index(inplace = True)
        d3 = pd.concat([base,min_aps],sort=True).reset_index(drop = True)
        d3["EVENT_RATE"] = d3.EVENT/d3.COUNT
        d3["NON_EVENT_RATE"] = d3.NONEVENT/d3.COUNT
        d3["DIST_EVENT"] = d3.EVENT/d3.sum().EVENT
        d3["DIST_NON_EVENT"] = d3.NONEVENT/d3.sum().NONEVENT
        d3["WOE"] = np.log(d3.DIST_EVENT/d3.DIST_NON_EVENT)
        d3["IV"] = (d3.DIST_EVENT-d3.DIST_NON_EVENT)*np.log(d3.DIST_EVENT/d3.DIST_NON_EVENT)
        d3["Iter"] = iter_new
        d3.sort_values('MIN_VALUE',inplace=True)
        d3.reset_index(drop=True,inplace=True)
        # All the edited data back to Final Information Values
        self.__all_iv_df = pd.concat([self.__all_iv_df,d3],sort=True)
        # Plot the recently changed variable
        plt_df = d3[pd.notnull(d3['MIN_VALUE'])]['WOE'].reset_index(drop=True)
        plt_df.plot(title = 'New WOE plot: '+ d3['VAR_NAME'][0],xticks = ([i for i in plt_df.index]))
        display(Markdown(f"### <font color=blue>{d3['VAR_NAME'][0].upper()} combined index {tups} in {iter_new} iteration</font>"))
        plt.show()
        display(HTML(d3[['WOE','IV','MIN_VALUE','MAX_VALUE','EVENT','NONEVENT','EVENT_RATE','NON_EVENT_RATE']].to_html()))
    def __replace_col(self,colval,colname,woe=True):
        tmp = self.__final_woe[self.__final_woe['VAR_NAME']==colname]
        tmp.reset_index(inplace=True)
        minvec = tmp['MIN_VALUE']
        maxvec = tmp['MAX_VALUE']
        woevec = tmp['WOE']
        try:
            nanwoe = list(woevec[pd.isnull(minvec)])[0]
        except IndexError:
            nanwoe = 0
        try:
            nanmin = list(minvec[pd.isnull(minvec)])[0]
        except IndexError:
            nanmin = 0
        opval=[]
        if woe:
            for comval in colval:
                for i in range(len(minvec)):
                    if pd.isnull(comval):
                        opval.append(round(nanwoe,3))
                        break
                    elif minvec[i]<=comval<=maxvec[i]:
                        opval.append(round(woevec[i],3))
                        break
        else:
            for comval in colval:
                for i in range(len(minvec)):
                    if pd.isnull(comval):
                        opval.append(round(nanmin,3))
                        break
                    elif minvec[i]<=comval<=maxvec[i]:
                        opval.append(minvec[i])
                        break
        return pd.Series(opval)
    def Display_WOE_Charts(self):
        """
        This Function display all the WOE charts of the dataframe. The number of charts displayed depends
        upon the class hyper-parameter 'ignore_threshold'. To switch between all and relevant variables,
        change the hyper-parameter accordingly.
        """
        for i in range(len(self.__rel_iv_vars)):
            self.__getcompcharts(i)
    def __getcompcharts(self,sno):
        colname = self.__rel_iv_vars[sno]
        maxval = max(self.__all_iv_df[self.__all_iv_df['VAR_NAME']==colname]['Iter'])
        min_df = self.__all_iv_df[(self.__all_iv_df['VAR_NAME']==colname) & (self.__all_iv_df['Iter']==0)]
        min_df.reset_index(drop=True,inplace=True)
        if maxval >0:
            d3 = self.__all_iv_df[(self.__all_iv_df['VAR_NAME']==colname) & (self.__all_iv_df['Iter']==maxval)]
            d3.reset_index(drop=True,inplace=True)
            display(Markdown(f"### <font color=blue>{sno} : {colname.upper()}</font>"))
            plt.figure(figsize=(12, 4))
            plt.subplot(1,2,1)
            plt_df = min_df[pd.notnull(min_df['MIN_VALUE'])]['WOE']
            plt_df.plot(title= f'Fine Classing WOE  Iteration: 0',xticks = ([i for i in plt_df.index]))
            plt.subplot(1,2,2)
            plt_df = d3[pd.notnull(d3['MIN_VALUE'])]['WOE']
            plt_df.plot(title=f'Coarse Classing WOE  Iteration: {maxval}',xticks = ([i for i in plt_df.index]))
            plt.tight_layout()
            plt.show()
            display(HTML(d3[['WOE','IV','MIN_VALUE','MAX_VALUE','EVENT','NONEVENT','EVENT_RATE','NON_EVENT_RATE']].to_html()))
        else:
            display(Markdown(f"### <font color=blue>{sno} : {colname.upper()}</font>"))
            plt_df = min_df[pd.notnull(min_df['MIN_VALUE'])]['WOE']
            plt_df.plot(title=f'Fine Classing WOE  Iteration: {maxval}',xticks = ([i for i in plt_df.index]))
            plt.show()
            display(HTML(min_df[['WOE','IV','MIN_VALUE','MAX_VALUE','EVENT','NONEVENT','EVENT_RATE','NON_EVENT_RATE']].to_html()))
