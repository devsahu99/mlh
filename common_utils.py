class common_utils:
    # !/usr/bin/env python
    # -*- coding: utf-8 -*-
    # Author: Devendra Kumar Sahu
    # Email: devsahu99@gmail.com
    # Sqliite DB related tasks
    """
    This function contains list of support utilities helful in regular data science work
        
    ------------------------------------------------------------
    Returns:
    Requested data as pandas dataframe
    
    ------------------------------------------------------------
    Approach:

    1. Create an instance of util function
         cmf = common_utils()

    2. Call individual functions
         cmf.Get_Quarter_End_Date('2023-05-23')
    ------------------------------------------------------------    
    """
    def __init__(self):
        self.__name = 'common_utils'
        
    def YM_Delta(self, year_month, delta=0, ym_format='%Y%m'):
        """
        This function return the delta of the date in Year-Month format

        ------------------------------------------------------------
        Parameters:
        year_month: input date in the given format
        delta: default:0, the number of months forward backward
        ym_format: the format of the given input date
        ------------------------------------------------------------
        Example:
            cmf = common_utils()
            cmf.YM_Delta('202310', -5)
        ------------------------------------------------------------    
        """
        year_month_dt = pd.to_datetime(year_month, format=ym_format)
        year_month_delta = dateutil.relativedelta.relativedelta(months=delta)
        return (year_month_dt+year_month_delta).strftime(ym_format)
    
    def Get_Quarter_End_Date(self, InputDate):
        """
        This function return the delta of the date in Year-Month format

        ------------------------------------------------------------
        Parameters:
        year_month: input date in the given format
        delta: default:0, the number of months forward backward
        ym_format: the format of the given input date
        ------------------------------------------------------------
        Example:
            cmf = common_utils()
            cmf.YM_Delta('202310', -5)
        ------------------------------------------------------------    
        """
        try:
            quarter_first_date = datetime(InputDate.year, (InputDate.quarter)*3-2, 1)
            quarter_last_date = quarter_first_date + relativedelta(months=3, days=-1)
            return quarter_last_date.strftime('%Y-%m-%d')
        except Exception as ex:
            print(datetime.now().replace(microsecond=0), " Date conversion to Quarter failed - exiting run")
            print(datetime.now().replace(microsecond=0), ex)
            sys.exit()
        return None
    
    def Get_Last_N_Quarters(self, quarterNG, n=4, gap='No'):
        """
        This function returns last N quarters into year-quarter format

        ------------------------------------------------------------
        Parameters:
        quarterNG: String
            input date in the year-quarter format
        n: Integer
            required number of last quarters 
        ------------------------------------------------------------
        Example:
            cmf = common_utils()
            cmf.Get_Last_N_Quarters('202310', n=5)
        ------------------------------------------------------------    
        """
        quarterNG = quarterNG.replace(' ', '')
        latestQuartersDT = pd.PeriodIndex([quarterNG], freq='Q').to_timestamp()
        ldt = latestQuartersDT[0]
        latestNQuartersNG = [str((ldt-pd.offsets.QuarterEnd(x,ldt)).to_period('Q')) for x in range(n)]
        if gap == 'No':
            return latestNQuartersNG
        return [x.replace('Q', ' Q') for x in latestNQuartersNG]

    def Get_Last_N_Quarter_Dates(self, quarterNG, n=4):
        """
        This function returns last N quarter dates into datetime format

        ------------------------------------------------------------
        Parameters:
        quarterNG: String
            input date in the year-quarter format
        ------------------------------------------------------------
        Example:
            cmf = common_utils()
            cmf.Get_Last_N_Quarter_Dates('202310', n=5)
        ------------------------------------------------------------    
        """
        dt = self.getLastNQuarters(quarterNG, n)
        return [self.Get_Quarter_End_Date(x) for x in pd.to_datetime(pd.Series(dt))]

    def Date_to_Quarter_Start_Date(self, InputDate):
        """
        This function returns any date to its quarter start date. Helpful in cases where quarterly trends are required

        ------------------------------------------------------------
        Parameters:
        InputDate: Datetime
            input date to be converted

        ------------------------------------------------------------
        Example:
            cmf = common_utils()
            cmf.Dateconversion(pd.to_datetime('2023-10-01'))
        ------------------------------------------------------------    
        """
        try:
            currQuarter = int(((InputDate.month - 1) / 3) + 1)
            #currQuarter = int(InputDate.quarter)
            dtFirstDay = datetime(InputDate.year, 3 * currQuarter - 2, 1)
            dtLastDay = dtFirstDay + relativedelta(months=3, days=-1)
            dtLastDay = dtLastDay.strftime('%Y-%m-%d')
            return dtLastDay

        except Exception as ex:
            sys.stdout = open("log.txt", "w")
            print(datetime.now().replace(microsecond=0), " Date conversion to Quarter failed - exiting run")
            print(datetime.now().replace(microsecond=0), ex)
            sys.exit()
        return None
