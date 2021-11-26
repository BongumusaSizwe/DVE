import pandas as pd
import seaborn as sns
import numpy as np
import scipy.cluster.hierarchy as shc
import matplotlib.pyplot as plt
from scipy import stats

from PIL import Image
import glob
import os.path
import clean_dataset

import folium
from folium.plugins import HeatMap
from IPython.display import IFrame
import time

from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait

os.environ['WDM_LOG_LEVEL'] = '0'

# add github PAT in case of API problems
# os.environ['GH_TOKEN'] = ''

# check if clean dataset file exists
if not os.path.exists('clean.csv'):
    print('producing clean dataset')
    clean_dataset.produce_clean()
else:
    print('clean dataset already produced')

#load dataset
df = pd.read_csv('clean.csv', delimiter=',', header=0, index_col=0)

# select columns to use when plotting the heatmap
df_hmap = df[['pickup_datetime', 'pickup_longitude', 'pickup_latitude']].copy()
df_hmap['day_of_week'] = pd.to_datetime(df_hmap['pickup_datetime']).dt.dayofweek #gives index of monday to sunday
df_hmap['hour_of_day'] = pd.to_datetime(df_hmap['pickup_datetime']).dt.hour

# Function to visualize the heatmap
def embed_map(map, filename):
    map.save(filename)
    return IFrame(filename, width='100%', height='500px')


# function to create heatmap
def make_map(first_day, last_day, start_time, end_time, df_tmp, title="title"):
    '''
        first_day: First day index to draw heat_map for
        last_day: Last day index to draw heat_map for
        start_time: Hour of the day to start heat map
        end_time: Hour of the day to end heat map
        df_tmp: Dataframe with the required dataset
    '''
    dow_dict = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    
    for i in range(first_day, last_day+1):
        for j in range(start_time, end_time + 1):
            # filter to include the specified params
            df_geo = df_tmp.loc[(df_tmp.day_of_week == i) & (df_tmp.hour_of_day == j)][['pickup_latitude', 'pickup_longitude']].copy()
            df_geo = df_geo.astype(np.float64)
            # instantiate map object
            pickup_map = folium.Map(location = [40.730610,-73.935242], tiles='openstreetmap', zoom_start=10)
            
            # plot heatmap
            # HeatMap(data = df_geo, radius = 10).add_to(drop_map)
            HeatMap(list(zip(df_geo.pickup_latitude.values, df_geo.pickup_longitude.values))).add_to(pickup_map)
            
            # get day of the week string from dow_dict
            d = dow_dict[i]
            
            #Add title
            title_html = f'''<h3 align="center" style="font-size:20px">
                        <b> NYC Cab Pickups at {j}:00 on {d}: {len(df_geo)} rides</b></h3>
                        '''
            pickup_map.get_root().html.add_child(folium.Element(title_html))
            
            # Save map
            embed_map(pickup_map, f'./question_1.4_files/html_maps_pickup/{title}/{i}_{j}_heatmap.html')


def make_pngs(first_day, last_day, first_hour, last_hour, title='title'):
  for i in range(first_day, last_day+1):
    for j in range(first_hour, last_hour):

      # set broswer to chrome if using chrome
      # browser = webdriver.Chrome()
      
      # If using firefox
      browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    #   browser = webdriver.PhantomJS()
      tmp_url = f'file:///home/cogeta/Supermagondovias/Course/Honors/Semester%202/IDVE/Assignments/DVE/Assignment%202/question_1.4_files/html_maps_pickup/{title}/{i}_{j}_heatmap.html'
      browser.get(tmp_url)

      #wait until the map fully loads(remove if using a faster machine)
      #WebDriverWait(browser, 10)
      time.sleep(5)      
      if j < 10:
          browser.save_screenshot(f'./question_1.4_files/png_maps_pickup/{title}/{i}_0{j}_heatmap.png')
      else:
      	  browser.save_screenshot(f'./question_1.4_files/png_maps_pickup/{title}/{i}_{j}_heatmap.png')
      
      browser.quit()


# png to gifs
def png_to_gif(path_to_images, save_file_path, duration=500):
    frames = []
    
    # Retrieve image files
    images = glob.glob(f'{path_to_images}')
    
    # Loop through image files to open, resize them and append them to frames
    for i in sorted(images): 
        im = Image.open(i)
        im = im.resize((550,389),Image.ANTIALIAS)
        frames.append(im.copy())
        
    # Save frames/ stitched images as .gif
    frames[0].save(f'{save_file_path}', format='GIF', append_images=frames[1:], save_all=True,
                   duration=duration, loop=0)



print('making weekdays morning heatmaps')
# heatmap for weekday, mornings
print('generating weekday html heatmaps')
make_map(0, 4, 5, 9,df_tmp=df_hmap, title="weekday_morning")
print('done')

print('converting html to png heatmaps')
make_pngs(0, 4, 5, 9, title='weekday_morning')
print('done')

# converting pngs to gifs
print('creating gifs for weekdays')
png_to_gif(path_to_images='./question_1.4_files/png_maps_pickup/weekday_morning/*.png', save_file_path = './question_1.4_files/plots/pickup_weekday_morning.gif', duration=500)
print('done')



print('making weekdays afternoon heatmaps')
# heatmap for weekday, afternoons
print('generating weekday html heatmaps')
#uses time from 
make_map(0, 4, 15, 20,df_tmp=df_hmap, title="weekday_afternoon")
print('done')

print('converting html to png heatmaps')
make_pngs(0, 4, 15, 20, title='weekday_afternoon')
print('done')

# converting pngs to gifs
print('creating gifs for weekdays')
png_to_gif(path_to_images='./question_1.4_files/png_maps_pickup/weekday_afternoon/*.png', save_file_path = './question_1.4_files/plots/pickup_weekday_afternoon.gif', duration=500)
print('done')


print('making weekends morning heatmaps')
# heatmap for weekend, mornings
print('generating weekday html heatmaps')
make_map(5, 6, 5, 9,df_tmp=df_hmap, title="weekend_morning")
print('done')

print('converting html to png heatmaps')
make_pngs(5, 6, 5, 9, title='weekend_morning')
print('done')

# converting pngs to gifs
print('creating gif for weekend')
png_to_gif(path_to_images='./question_1.4_files/png_maps_pickup/weekend_morning/*.png', save_file_path = './question_1.4_files/plots/pickup_weekend_morning.gif', duration=500)
print('done')



print('making weekend afternoon heatmaps')
# heatmap for weekend, afternoons
print('generating weekend html heatmaps')
#uses time from 
make_map(5, 6, 15, 20,df_tmp=df_hmap, title="weekend_afternoon")
print('done')

print('converting html to png heatmaps')
make_pngs(5, 6, 15, 20, title='weekend_afternoon')
print('done')

# converting pngs to gifs
print('creating gifs for weekdays')
png_to_gif(path_to_images='./question_1.4_files/png_maps_pickup/weekend_afternoon/*.png', save_file_path = './question_1.4_files/plots/pickup_weekend_afternoon.gif', duration=500)
print('done')




# print('making weekdays heatmap')
# # heatmap for weekend, afternoons
# print('generating weekdays html heatmaps')
# #uses time from 00:00 to 23
# make_map(0, 4, 0, 23,df_tmp=df_hmap, title="weekdays")
# print('done')

# print('converting html to png heatmaps')
# make_pngs(0, 4, 0, 23, title='weekdays')
# print('done')

# # converting pngs to gifs
# print('creating gifs for weekdays')
# png_to_gif(path_to_images='./question_1.4_files/png_maps_pickup/weekdays/*.png', save_file_path = './question_1.4_files/plots/pickup_weekdays.gif', duration=500)
# print('done')



# print('making weekend heatmaps')
# # heatmap for weekend, afternoons
# print('generating weekend html heatmaps')
# #uses time from 
# make_map(5, 6, 0, 23,df_tmp=df_hmap, title="weekend_afternoon")
# print('done')

# print('converting html to png heatmaps')
# make_pngs(5, 6, 15, 20, title='weekend_afternoon')
# print('done')

# # converting pngs to gifs
# print('creating gifs for weekdays')
# png_to_gif(path_to_images='./question_1.4_files/png_maps_pickup/weekend_afternoon/*.png', save_file_path = './question_1.4_files/plots/pickup_weekend_afternoon.gif', duration=500)
# print('done')
