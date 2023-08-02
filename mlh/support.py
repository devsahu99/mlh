import pandas as pd
import pandas.core.algorithms as algos
import scipy.stats.stats as stats
import re
from pandas import Series
import numpy as np
import random
from IPython.display import display, HTML, Markdown
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV, StratifiedKFold, RandomizedSearchCV, train_test_split
from sklearn.metrics import accuracy_score,classification_report,confusion_matrix,roc_curve,auc,precision_recall_curve,make_scorer,recall_score,precision_score
import scikitplot as skplt

class support:
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    # Author: Devendra Kumar Sahu
    # Email: devsahu99@gmail.com
    """
    This function contains additional support functions to help build machine learning models.
    which includes finding irrelavant features, grid search, getting precision-recall scores,
    and performance plots.
    
    Example:
    
    from sklearn.model_selection import train_test_split
    from xgboost import XGBClassifier
    from mlh import support
    import pandas as pd

    myhelp = support()

    df = pd.read_csv(r'Kaggle_Titanic_Train.csv')

    df = df[['Survived', 'Pclass', 'Sex', 'Age', 'SibSp', 'Parch','Fare', 'Embarked']]

    pred_var='Survived'

    # To get the dropping features
    myhelp.Get_Drop_Feature_Names(df,pred_var,missing_threshold=.09)

    # For grid search to obtain best hyper-parameters
    df = pd.get_dummies(df,drop_first=True)
    df.fillna(method='ffill',inplace=True)

    model_xgb = XGBClassifier(objective='binary:logistic',eval_metric='error',seed=42,
                   max_depth=10,colsample_bytree=.9,n_estimators=100)

    param_grid = {'scale_pos_weight':[6],
    'learning_rate':[.4],
    'max_depth': [13],
    'min_child_weight': [.1,1,20], #.1,1,20
    }

    grid_xg_ps = myhelp.gs_find(df,pred_var,model_xgb,param_grid,random_search=False)

    # Fitting The model
    X_train, X_test, y_train, y_test = train_test_split(df.drop(pred_var,axis=1), df[pred_var], test_size=0.30, random_state=42)
    model_xgb.fit(X_train,y_train)

    # Predict the probabilities
    pred_prob = model_xgb.predict_proba(X_test)

    # Get Precision-Recall Scores
    pr_scores = myhelp.Get_Precision_Recall_Values(pred_prob,y_test)

    # Get confusion-matrix and other plots
    myhelp.Model_Output_Plots(pred_prob,y_test,rocplot=True)
    
    """
    def __init__(self):
        #initiating the class
        self.__mode=1
    def Grid_Search(self,df,pred_var,clf,param_grid,refit_score='precision_score',random_search=True,folds=10,iters=20,train_split=.3,split_state=99):
        """
        This helps is doing grid search. The default functionality is defined to 
        work on all the available cores for faster searching.

        Parameters:
        ------------------------------------------------------------
        df: pandas dataframe
            The dataframe for modelling
        
        clf: classifier
            reference of the classifier
            
        param_grid: dictionary
            Parameters grid
            
        refit_score: string
            refitting score value. Default is 'precision_score'. Allowed values are:
                'precision_score'
                'recall_score'
                'accuracy_score'
                
        random_search:Boolean
            condition whether the grid search should be random or sequential.
            Sequential search takes very long time but very effective in getting optimum 
            hyper-parameters
            
        folds:int
            Number of folds for cross-validation during grid search
            
        iters:int
            Number of iteration during random-search. it is not required in the case of 
            sequential grid search
            
        train_split: float
            Train test split ratio for the internal grid search splitting
        
        split_state: int
            seed for randomized internal splitting, this is required to get reproducible results
            
        ------------------------------------------------------------
        Returns:
        The grid search object.
        
        Example:
        ------------------------------------------------------------
        from xgboost import XGBClassifier
        from mlh import support
        import pandas as pd

        myhelp = support()

        df = pd.read_csv(r'Kaggle_Titanic_Train.csv')

        df = df[['Survived', 'Pclass', 'Sex', 'Age', 'SibSp', 'Parch','Fare', 'Embarked']]

        pred_var='Survived'

        # To get the dropping features
        myhelp.Get_Drop_Feature_Names(df,pred_var,missing_threshold=.09)

        # For grid search to obtain best hyper-parameters
        df = pd.get_dummies(df,drop_first=True)
        df.fillna(method='ffill',inplace=True)

        model_xgb = XGBClassifier(objective='binary:logistic',eval_metric='error',seed=42,
                       max_depth=10,colsample_bytree=.9,n_estimators=100)

        param_grid = {'scale_pos_weight':[6],
        'learning_rate':[.4],
        'max_depth': [13],
        'min_child_weight': [.1,1,20], #.1,1,20
        }

        grid_xg_ps = myhelp.Grid_Search(df,pred_var,model_xgb,param_grid,random_search=False)
        
        """
        X_train, X_test, y_train, y_test = train_test_split(df.drop(pred_var,axis=1), df[pred_var], test_size=train_split, random_state=split_state)
        scorers = {
            'precision_score': make_scorer(precision_score),
            'recall_score': make_scorer(recall_score),
            'accuracy_score': make_scorer(accuracy_score)
        }
        skf = StratifiedKFold(n_splits=folds)
        if random_search:
            grid_search = RandomizedSearchCV(clf, param_grid, scoring=scorers, refit=refit_score,cv=skf, n_iter=iters, return_train_score=True, n_jobs=-1)
        else:
            grid_search = GridSearchCV(clf, param_grid, scoring=scorers, refit=refit_score,cv=skf, return_train_score=True, n_jobs=-1)
        grid_search.fit(X_train.values, y_train.values)
        y_pred = grid_search.predict(X_test.values)
        print('Best params for {refit_score}')
        print(grid_search.best_params_)
        print(f'\nConfusion matrix of Random Forest optimized for {refit_score} on the test data')
        print(pd.DataFrame(confusion_matrix(y_test, y_pred),columns=['pred_neg', 'pred_pos'], index=['neg', 'pos']))
        return grid_search
    
    def __adjusted_classes(self, y_scores, t):
        return [1 if y >= t else 0 for y in y_scores]

    def Model_Output_Plots(self,pred_probs,y_test,t=0.5,cf_matrix=True,rocplot=False,skplot=False,prcplot=False,thrplot=False):
        """
        This utility prints confusion matrix and displays multiple relevant charts.

        Parameters:
        ------------------------------------------------------------
        pred_prob: matrix
            The prediction probabilities obtained from the scikit-learn function pred_prob
        
        y_test: series
            Values of the test variable against which precision-recall has to be calculated. 
            The length of this should be equal to pred_prob matrix 
        
        t: float
            Threshold value for confusion matrix and other plots. Default is 0.5
        
        cf_matrix: Boolean
            Condition to print confusion matrix. Default is True
            
        rocplot: Boolean
            Condition to plot ROC curve. Default is False
        
        skplot: Boolean
            Condition to plot scikitplot. Default is False
        
        prcplot: Boolean
            Condition to plot precision-recall area-curve. Default is False
        
        thrplot: Boolean
            Condition to plot precision-recall curve based on each threshold value. Default is False
            This plot has cutoff limits for the abrupt reductions is number of favorable cases.
        
        ------------------------------------------------------------
        Returns:
        Confusion matrix and the conditional plots
        
        """
        try:
            pred_prob = pred_probs[::,1]
        except:
            pred_prob = pred_probs
        y_pred_adj = self.__adjusted_classes(pred_prob, t)
        if cf_matrix:
            print(classification_report(y_test,y_pred_adj,target_names=['class 0','class 1']))
            print(f'Accuracy Score: {accuracy_score(y_test,y_pred_adj)}')
            print(f'Confusion Matrix: {confusion_matrix(y_test,y_pred_adj)}')
        fpr, tpr, threshold = roc_curve(y_test, pred_prob)
        roc_auc = auc(fpr, tpr)
        if rocplot:
            plt.figure(figsize=(8, 4))
            plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
            plt.legend(loc = 'lower right')
            plt.plot([0, 1], [0, 1],'r--')
            plt.xlim([0, 1])
            plt.ylim([0, 1])
            plt.ylabel('True Positive Rate')
            plt.xlabel('False Positive Rate')
            plt.show()
        p, r, thresholds = precision_recall_curve(y_test, pred_prob)
        if skplot:
            plt.figure(figsize=(8, 4))
            #Plot the skplot using sklearn's skplot
            skplt.metrics.plot_roc_curve(y_test,pred_probs)
        if prcplot:
            # plot the Precision Recall Curve
            plt.figure(figsize=(8,8))
            plt.title("Precision and Recall curve ^ = current threshold")
            plt.step(r, p, color='b', alpha=0.2,where='post')
            plt.fill_between(r, p, step='post', alpha=0.2,color='b')
            #plt.ylim([0.5, 1.01]);
            #plt.xlim([0.5, 1.01]);
            plt.xlabel('Recall');
            plt.ylabel('Precision');
            # plot the current threshold on the line
            close_default_clf = np.argmin(np.abs(thresholds- t))
            plt.plot(r[close_default_clf], p[close_default_clf], '^', c='k',markersize=15)
            plt.show()
        if thrplot:
            cutoff = np.argmax(p[:-1])+1
            plt.figure(figsize=(8, 8))
            plt.title("Precision and Recall Scores as a function of the decision threshold")
            plt.plot(thresholds[0:cutoff], p[0:cutoff], "b--", label="Precision")
            plt.plot(thresholds[0:cutoff], r[0:cutoff], "g-", label="Recall")
            plt.ylabel("Score")
            plt.xlabel("Decision Threshold")
            plt.legend(loc='best')
            plt.show()
    # Add prediction probability to dataframe
    def Get_Precision_Recall_Values(self,pred_prob,y_test):
        """
        This utility helps is getting precision-recall values at multiple thresholds.

        Parameters:
        ------------------------------------------------------------
        pred_prob: matrix
            The prediction probabilities obtained from the scikit-learn function pred_prob
        
        y_test: series
            Values of the test variable against which precision-recall has to be calculated. 
            The length of this should be equal to pred_prob matrix 

        ------------------------------------------------------------
        Returns:
        Dataframe containing the thresholds, precision, recall, accuracy and f1-scores.
        
        """
        attr_dt_val = pd.DataFrame({'pred_proba':pred_prob[::,1],'target1':y_test})
        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5,0.6,0.7,0.8,0.9]
        from scipy import arange
        l1 =[]
        for threshold in thresholds: 
            attr_dt_val['pred'] = np.where(attr_dt_val['pred_proba'] >= threshold, 1, 0)
            cf_mat = confusion_matrix(y_test, attr_dt_val['pred'])
            accuracy = (cf_mat[0][0]+cf_mat[1][1])/(sum(cf_mat[0])+sum(cf_mat[1]))
            records = sum(attr_dt_val['pred'])
            all_records = len(attr_dt_val['pred'])
            records_share = round(records/all_records,3)
            b=classification_report(attr_dt_val['target1'].values, attr_dt_val['pred'])
            a=b.split(" ")
            e = [x for x in a if x]
            for i in range(len(e)):
                if (e[i] =='0'):
                    Precision_0= e[i+1]
                    Recal_0=e[i+2]
                    F1_Score_0=e[i+3]
                elif (e[i]=='1'):
                    Precision_1= e[i+1]
                    Recal_1=e[i+2]
                    F1_Score_1=e[i+3]
            l1.append([threshold ,Precision_0,Precision_1,Recal_0,Recal_1,F1_Score_0,F1_Score_1,accuracy,records,all_records,records_share])
        result = pd.DataFrame(l1)
        result.columns= ['Threshold','Precision_0','Precision_1','Recal_0','Recal_1','F1_Score_0','F1_Score_1','Accuracy','Records','All_Records','Records_Share']
        return result
    
    # Remove Constant Features
    def __constance_columns(self):
        df = self.__df.copy()
        colsToRemove = []
        cols = df.columns
        float_features = np.where(df.dtypes!=np.object)[0]
        for col in cols[float_features]:
            if col != self.__pred_var:
                if df[col].std() == 0: 
                    colsToRemove.append(col)
        return colsToRemove
    # Remove Duplicate Columns
    def __duplicate_columns(self):
        df = self.__df.copy()
        groups = df.columns.to_series().groupby(df.dtypes).groups
        dups = []
        for t, v in groups.items():
            cs = df[v].columns
            vs = df[v]
            lcs = len(cs)
            for i in range(lcs):
                ia = vs.iloc[:,i].values
                for j in range(i+1, lcs):
                    ja = vs.iloc[:,j].values
                    if np.array_equal(ia, ja):
                        dups.append(cs[i])
                        break
        return dups
    # Drop Sparse Data
    def __drop_sparse(self):
        df = self.__df.copy()
        colsToRemove = []
        flist = [x for x in df.columns if not x in [self.__pred_var]]
        for col in flist:
            if len(df[col].value_counts())<self.__sparseCounts:
                colsToRemove.append(col)
        return colsToRemove
    # Drop Missing Information
    def __getmissing(self):
        df = self.__df.copy()
        colsToRemove = []
        rows = df.shape[0]
        cols=[x for x in df.columns if not x in [self.__pred_var]]
        for col in cols:
            na_vals = df[col].isna().sum()
            na_per = na_vals/rows
            if na_per>self.__missing_threshold:
                colsToRemove.append(col)
        return colsToRemove
    
    def Get_Drop_Feature_Names(self,df,pred_var,missing_threshold=.95):
        """
        This utility helps is getting non-essential features in a dataframe for classification problems.
        The function takes evaluates each features and returns curated names of features to be removed.
        
        Parameters:
        ------------------------------------------------------------
        df: pandas dataframe
            The reference of the dataframe to be evaluated
        
        pred_var: string
            Name of the classification target variable 
        
        missing_threshold: float
            The threshold beyond which if the feature has missing values then that will considered for removal
        
        ------------------------------------------------------------
        Returns:
        List of features to removed and another list of duplicate features which could be further analysed or removed.
        
        """
        self.__df = df
        self.__pred_var = pred_var
        self.__missing_threshold = missing_threshold
        self.__sparseCounts = 2
        colsRemove = []
        colsRemove.extend(self.__constance_columns())
        colsRemove.extend(self.__drop_sparse())
        colsRemove.extend(self.__getmissing())
        dropCols = {'Drop_Features':list(set(colsRemove)),'duplicates':self.__duplicate_columns()}
        return dropCols
