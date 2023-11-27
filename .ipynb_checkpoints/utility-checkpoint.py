import re
import pandas as pd
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

def add_priority_numbers(df, column_name):
    column_counts = df[column_name].value_counts()
    total_number_of_unique = len(column_counts)
    priority_numbers = {value: total_number_of_unique - rank + 1 for rank, value in enumerate(column_counts.index, start=1)}
    df[column_name + '_priority'] = df[column_name].map(priority_numbers)
    return df

def fill_in_colum_with_unknown(df, column_name):
    column_values = df[column_name].fillna('Unknown')
    df[column_name] = column_values
    return  df

def fill_in_colum_with_postal_code_unknown(df):
    column_values = df['Postal Code'].fillna('00000.0')
    df['Postal Code'] = column_values
    return  df

def execute_one_hod_encoder(df, column_name):
    ohe_make = OneHotEncoder()
    encoded_cafv = ohe_make.fit_transform(df[column_name].values.reshape(-1, 1)).toarray()
    ohe_df = pd.DataFrame(encoded_cafv, columns=ohe_make.get_feature_names_out())
    df = pd.concat([df, ohe_df], axis=1)
    return df

def execute_label_encoder(df, column_name):
    le_make = LabelEncoder()
    encoded_values = le_make.fit_transform(df[column_name])
    df[column_name] = encoded_values
    return  df

def convert_vin_number_to_hach(df, column_name):
    #column_counts = df[column_name].value_counts()
    #total_number_of_unique = len(column_counts)
    #hash_numbers = {hash(value) for value in df[column_name]}
    df[column_name] = df[column_name].apply(lambda value: hash(value))
    #df[column_name] = hash_numbers
    return df

def extract_coordinates(x, index):
    coords = re.findall(r'-?\d+\.\d+', x)
    if len(coords) >= 2:
        return float(coords[index])
    else:
        return None

# unpack the coordinates 
def unpack_coordinates(df):
    # Convert the 'Vehicle Location' column to string type
    df['Vehicle Location'] = df['Vehicle Location'].astype(str)
    df['Longitude'] = df['Vehicle Location'].apply(lambda x: extract_coordinates(x, 0))
    df['Latitude'] = df['Vehicle Location'].apply(lambda x: extract_coordinates(x, 0))
    return df

def fill_in_colum_with_point_unknown(df):
    column_values = df['Vehicle Location'].fillna('POINT (000.00000000000000 00.00000000000000)')
    df['Vehicle Location'] = column_values
    return  df

def fill_in_colum_with_zero(df, column_name, to_fill_value):
    column_values = df[column_name].fillna(to_fill_value)
    df[column_name] = column_values
    return  df

def create_price_range_category(df, column='Base MSRP'):
    def categorize_price(price):
        if 0 <= price <= 25000 :
            return 0
        elif 25000 < price <= 40000:
            return 1
        elif 40000 < price <= 60000:
            return 2
        else:
            return 3

    df['Price_Range_Category'] = df[column].apply(categorize_price)
    return df


def calculate_mean_value(df):
    electric_range_without_zero = df[df['Electric Range'] != 0.0]
    electric_range_only_zero = df[df['Electric Range'] == 0.0]
    group_electrical_range = electric_range_without_zero.groupby(['Electric Vehicle Type', 'Make'], as_index=False)['Electric Range'].mean()

    for index, row in group_electrical_range.iterrows():
        mask = (df['Electric Range'] == 0.0) & (df['Make'] == row['Make'])
        df.loc[mask, 'Electric Range'] = row['Electric Range']
        #mask = (electric_vehicles['Electric Range'] == 0.0) & (electric_vehicles['Model'] == row['Model'])
        #electric_vehicles.loc[mask, 'Electric Range'] = row['Electric Range']
    return df


PHEV = 'Plug-in Hybrid Electric Vehicle (PHEV)'
BEV = 'Battery Electric Vehicle (BEV)'

# This function define the same category for PHEV and BEV unsing different values ranges
def create_electric_range_category(df, column='Electric Range'):
    """
    """
    def categorize_range(columns):
        electric_range = columns['Electric Range']
        electric_vehicle_type = columns['Electric Vehicle Type']
        if electric_range == 0:
            return 0
        elif 0.0 < electric_range < 50 and electric_vehicle_type == BEV:
            return 1 #10 #very Short
        elif 50 <= electric_range <= 100 and electric_vehicle_type == BEV:
            return 2 #20 #Short
        elif 100 < electric_range <= 300 and electric_vehicle_type == BEV:
            return 3 #30 #Medium
        elif 300 < electric_range <= 550 and electric_vehicle_type == BEV:
            return 4 #40 #long
        elif 550 < electric_range and electric_vehicle_type == BEV:
            return 5 #50 # Extry long
        elif 0.0 < electric_range < 10 and electric_vehicle_type == PHEV:
            return 1 #very Short
        elif 10 <= electric_range <= 50 and electric_vehicle_type == PHEV:
            return 2 #Short
        elif 50 < electric_range <= 80 and electric_vehicle_type == PHEV:
            return 3 #Medium
        elif 80 < electric_range <= 160 and electric_vehicle_type == PHEV:
            return 4 #long
        elif 160 < electric_range and electric_vehicle_type == PHEV:
            return 5 # Extry lo
        else:
            return -1.0

    df['Electric_Range_Category'] = df.apply(categorize_range, axis=1)
    return df

# This function define the diferent category for PHEV and BEV unsing different values ranges
def create_electric_range_category_for_bev_and_phev(df, column='Electric Range'):
    def categorize_range(columns):
        electric_range = columns['Electric Range']
        electric_vehicle_type = columns['Electric Vehicle Type']
        if electric_range == 0.0 and electric_vehicle_type == BEV:
            return 0
        elif 0.0 < electric_range < 50 and electric_vehicle_type == BEV:
            return 1 #10 #very Short
        elif 50 <= electric_range <= 100 and electric_vehicle_type == BEV:
            return 2 #20 #Short
        elif 100 < electric_range <= 300 and electric_vehicle_type == BEV:
            return 3 #30 #Medium
        elif 300 < electric_range <= 550 and electric_vehicle_type == BEV:
            return 4 #40 #long
        elif 0.0 < electric_range <= 6 and electric_vehicle_type == PHEV:
            return 5 #very Short
        elif 6 < electric_range <= 30 and electric_vehicle_type == PHEV:
            return 6 #Short
        elif 30 < electric_range <= 80 and electric_vehicle_type == PHEV:
            return 7 #Medium
        elif 80 < electric_range <= 160 and electric_vehicle_type == PHEV:
            return 8 #long
        else:
            return -1.0

    df['Electric_Range_Category'] = df.apply(categorize_range, axis=1)
    return df

def create_electric_range_category_only_one(df, column='Electric Range'):
    def categorize_range(columns):
        electric_range = columns['Electric Range']
        #electric_vehicle_type = columns['Electric Vehicle Type']
        if electric_range == 0.0:
            return 1
        elif 0.0 < electric_range < 50:
            return 2 #10 #very Short
        elif 50 <= electric_range <= 100: 
            return 3 #20 #Short
        elif 100 < electric_range <= 300:
            return 4 #30 #Medium
        elif 300 < electric_range <= 550:
            return 5 #40 #long
        else:
            return -1.0

    df['Electric_Range_Category'] = df.apply(categorize_range, axis=1)
    return df