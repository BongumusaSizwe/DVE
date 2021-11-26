# Python file, will produce a clean dataset, using the questions already answered so far
# to avoid pushing of large files

import os
import pandas as pd
import seaborn as sns
import numpy as np
import scipy.cluster.hierarchy as shc
import math
from scipy import stats

from pandas.tseries.holiday import USFederalHolidayCalendar as calendar

def produce_clean():
    df = pd.read_csv('nyc_taxis.csv', delimiter=',', header=0, index_col=0)

    # # Qusetion1.2

    def haversine_dist(lon1, lat1, lon2, lat2):
        """Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        
        :params lon1: First point longitude in degrees
        :params lat1: First point latitude in degrees
        :params lon2: Second point longitude in degress
        :params lat2: Second point latitude in degrees
        
        :returns distance in kilometers
        """
        # Convert decimal degrees to radians 
        lon1 = np.deg2rad(lon1)
        lat1 = np.deg2rad(lat1)
        lon2 = np.deg2rad(lon2)
        lat2 = np.deg2rad(lat2)

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        r = 6371 # Radius of earth(km)
        
        distance = c*r
        
        return np.round(distance,decimals=3)



    df['trip_distance(km)'] = haversine_dist(df['pickup_longitude'], df['pickup_latitude'], 
                df['dropoff_longitude'], df['dropoff_latitude'])


    # ## Create Average speed column
    df['avg_speed(km/hr)'] = df['trip_distance(km)']/(df['trip_duration'].apply(lambda x: x/3600))

    # ## Create date columns

    # Year
    df['trip_year'] = pd.to_datetime(df['pickup_datetime']).dt.year

    # Month
    df['trip_month'] = pd.to_datetime(df['pickup_datetime']).dt.month

    # Day_of_week
    df['trip_weekday'] = pd.to_datetime(df['pickup_datetime']).dt.weekday


    # # Question 1.1

    # **Inital observations:**
    # 
    # * From the plots above we can see that there clearly some outliers in the dataset.
    # * The trip duration plot: It looks like the outliers occur from around $2.0\times 10^{6}$seconds. This is roughly equal to 555 hours. This is not really possible.
    # * The trip distance plot: Some of the values from above 200km could be outliers but we can investigate further.
    # * The average speed plot could have values influenced by the outliers in the trip duration or trip distance.

    # ## 1. Investigate trip duration

    # **Z-score**

    z_score_1 = np.abs(stats.zscore(df['trip_duration']))
    thresh = 3

    # position of the outlier
    filtered_entries = (z_score_1 > 3)
    outlier_1 = df[filtered_entries]
    print('Outliers found',len(outlier_1))


    # Here we can see that my inital assumption about some of the larger outliers was correct. What my inital observation missed was some the lower outliers that could occur.

    # ## 2. Investigate trip distance

    # **Z-score**

    z_score_2 = np.abs(stats.zscore(df['trip_distance(km)']))
    thresh = 3
    # position of the outlier
    filtered_entries = (z_score_2 > thresh)
    outlier_2 = df[filtered_entries]
    print('Outliers found',len(outlier_2))


    # ## 2. Investigate average speed

    # **Z-score**
    z_score_3 = np.abs(stats.zscore(df['avg_speed(km/hr)']))
    thresh = 3

    # position of the outlier
    filtered_entries = (z_score_3 > thresh)
    outlier_3 = df[filtered_entries]
    print('Outliers found',len(outlier_3))

    # ## Droping the outliers from the three feauture observations

    # Drop the rows
    outliers = outlier_1 + outlier_2 + outlier_3
    df = df.drop(outliers.index)


    # # Qusetion 1.3

    # ### Question 1.3.1


    # ### Question 1.3.2

    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])



    df['trip_hour'] = df['pickup_datetime'].dt.hour



    peak_hour_of_day = df.groupby('trip_weekday').agg({'trip_hour':pd.Series.mode})


    # On a Monday most people pickup at 6pm <br>
    # On a Tuesday most people pickup at 6pm <br>
    # On a Wednesday most people pickup at 7pm <br>
    # On a Thursday most people pickup at 9pm <br>
    # On a Friday most people pickup at 7pm <br>
    # On a Saturday most people pickup at 11pm <br>
    # On a Sunday most people pickup at 12am

    # Most people pickup at 6pm and 7pm <br>
    # This can be due to most people are coming back from work at that time

    # ### QUestion 1.3.3


    hours_in_day = df.groupby('trip_weekday')['trip_hour'].apply(list)


    # Weekdays

    plt.hist(hours_in_day[0], 24,label='Mon',alpha = 0.5)
    plt.hist(hours_in_day[1], 24,label='Tues',alpha = 0.5)
    plt.hist(hours_in_day[2], 24,label='Wednes',alpha = 0.5)
    plt.hist(hours_in_day[3], 24,label='Thurs',alpha = 0.5)
    plt.hist(hours_in_day[4], 24,label='Fri',alpha = 0.5)
    plt.legend()


    # Weekends

    plt.hist(hours_in_day[5], 24,label='Sat',alpha = 0.5)
    plt.hist(hours_in_day[6], 24,label='Sun',alpha = 0.5)
    plt.legend()


    # Weekday VS Weekend

    plt.hist(hours_in_day[0], 24,label='Mon',alpha = 0.5)
    plt.hist(hours_in_day[5], 24,label='Sat',alpha = 0.5)
    plt.legend()


    # On weekends most people like to pickup at early Morning 12am to 5am. <br>
    # Saturday is similar to weekdays but there are more pickups in the early hours 12am to 5am <br>
    # On Sunday after 6pm most people don't pickup anymore. <br>
    # The early pickups on weekend might be due to people traveling to vist there families, it can also be due to people partying on the weekend. <br>
    # We can also see that not much pickups happen at 5am to 10am at the weekends, this can be due to people not going to work.

    # ### Question 1.3.4

    cal = calendar()
    Holidays = cal.holidays(start=df['pickup_datetime'].min(), end=df['pickup_datetime'].max())
    df['Holiday'] = df['pickup_datetime'].dt.date.astype('datetime64').isin(Holidays)


    Holidays_df = df[df['Holiday'] == True]



    hours_in_day_holidays = Holidays_df.groupby('trip_weekday')['trip_hour'].apply(list)


    plt.hist(hours_in_day_holidays[0], 24,label='Mon_Holiday',alpha = 0.5)
    plt.hist(hours_in_day[0], 24,label='Mon_regular',alpha = 0.5)
    plt.legend()


    # Compared to a noraml Monday, the one on Holiday indicate that they are far less pickups then normal. <br>
    # This shows that most people don't work or travel on Holidays

    # ### Question 1.3.5


    day_speed = df[['pickup_datetime','avg_speed(km/hr)']]

    # In[44]:


    day_speed_df = day_speed.groupby(pd.Grouper(key='pickup_datetime', freq='60min')).mean().dropna()

    # From the graphs it is seen that at around 5am to 8am the highest average speeds are archieved around 22km/hr to 27km/hr. This can be caused by people rushing to work. <br>
    # The slowest speeds are around 5pm to 8pm. This is when the taxis travel the slowest below 14km/hr. This can be due to traffic when everyone is returning from work and because people are not necessary in a rush when returning from work.




    ## Save df as clean

    df.to_csv('clean.csv')

if __name__== '__main__':
    produce_clean()