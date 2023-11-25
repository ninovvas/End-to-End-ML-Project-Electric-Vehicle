import re
import pandas as pd
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

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

def convert_vin_number_to_hach(df, column_name):
    #column_counts = df[column_name].value_counts()
    #total_number_of_unique = len(column_counts)
    #hash_numbers = {hash(value) for value in df[column_name]}
    df[column_name] = df[column_name].apply(lambda value: hash(value))
    #df[column_name] = hash_numbers
    return df