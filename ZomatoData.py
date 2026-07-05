# import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('dark_background')

# import data
df = pd.read_csv(r"C:\Users\HARSHIT RAJ\Downloads\zomato.csv (1)\zomato.csv")
df.head()

df.shape
#extracting shape

df.columns
#extracting column

# removing unwanted columns
df = df.drop(['url', 'address', 'phone', 'menu_item', 'dish_liked', 'reviews_list'], axis = 1)
df.head()

df.info()
#extrating information

# removing all the duplicates
df.drop_duplicates(inplace = True)
df.shape


df['rate'].unique()

# Removing "NEW" , "-" and "/5" from Rate Column
def handlerate(value):
    if(value=='NEW' or value=='-'):
        return np.nan
    else:
        value = str(value).split('/')
        value = value[0]
        return float(value)
    
df['rate'] = df['rate'].apply(handlerate)
df['rate'].head()

#Filling Null Values in Rate Column with Mean
df['rate'].fillna(df['rate'].mean(), inplace = True)
df['rate'].isnull().sum()

df.info()
#extracting information

# Dropping Null Values
df.dropna(inplace = True)
df.head()

# renaming the column
df.rename(columns = {'approx_cost(for two people)':'Cost2plates', 'listed_in(type)':'Type'}, inplace = True)
df.head()


df['location'].unique()
#extracting unique location

df['listed_in(city)'].unique()
#extracting unique city

# drop listed in city as both have same value and doing same work
df = df.drop(['listed_in(city)'], axis = 1)

df['Cost2plates'].unique()
#extracting unique cost 2 plates

# removing comma from cost2plates

def handlecomma(value):
    value = str(value)
    if ',' in value:
        value = value.replace(',', ' ')
        return float(value)
    else:
        return float(value)
    
df['Cost2plates'] = df['Cost2plates'].apply(handlecomma)
df['Cost2plates'].unique()

df.head()


# cleaning rest type
rest_types = df['rest_type'].value_counts(ascending  = False)
rest_types

rest_types_lessthan1000 = rest_types[rest_types<1000]
rest_types_lessthan1000

# if data less than 1000 in rest type, sum them all and count as others
def handle_rest_type(value):
    if(value in rest_types_lessthan1000):
        return 'others'
    else:
        return value
        
df['rest_type'] = df['rest_type'].apply(handle_rest_type)
df['rest_type'].value_counts()

#cleaning all the location
location = df['location'].value_counts(ascending  = False)

location_lessthan300 = location[location<300]



def handle_location(value):
    if(value in location_lessthan300):
        return 'others'
    else:
        return value
        
df['location'] = df['location'].apply(handle_location)
df['location'].value_counts()

# cleaning cuisine
cuisines = df['cuisines'].value_counts(ascending  = False)


cuisines_lessthan100 = cuisines[cuisines<100]



def handle_cuisines(value):
    if(value in cuisines_lessthan100):
        return 'others'
    else:
        return value
        
df['cuisines'] = df['cuisines'].apply(handle_cuisines)
df['cuisines'].value_counts()

df.head()

#---------- data cleaned-----------------

# ----------Visualization-------------

#Count Plot of Various Locations  
plt.figure(figsize = (16,10))
ax = sns.countplot(df['location'])
plt.xticks(rotation=0)

#Visualizing Online Order
plt.figure(figsize = (6,6))
sns.countplot(df['online_order'], palette = 'inferno')

# book table
plt.figure(figsize = (6,6))
sns.countplot(df['book_table'], palette = 'rainbow')

# boxplot of online order and rate
plt.figure(figsize = (6,6))
sns.boxplot(x = 'online_order', y = 'rate', data = df)

# book table and rate
plt.figure(figsize = (6,6))
sns.boxplot(x = 'book_table', y = 'rate', data = df)

# type and rate
plt.figure(figsize = (14, 8))
sns.boxplot(x = 'Type', y = 'rate', data = df, palette = 'inferno')

