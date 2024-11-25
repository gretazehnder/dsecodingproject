import pandas as pd

# This function converts coordinates like '13.14E' or '13.14S' to float values.'E' and 'N' are positive, 'W' and 'S' are negative.
    
def convert_to_float(coord):
    if 'E' in coord or 'N' in coord:
        return float(coord[:-1]) #removing the last character of the string, leaving just the number part and converting this string into a float (a decimal number).
    else:
        'W' in coord or 'S' in coord
        return -float(coord[:-1]) #same as before, but also adding a - sign in front to make it negative.

def st_load_data(filepath):
    data = pd.read_csv(filepath)
    
    # Extracting 'Year' from date
    data['Year'] = pd.to_datetime(data['dt'], errors='coerce').dt.year #converting the values in the 'dt' column to datetime format, and creates a new column in the DataFrame called Year that stores these extracted year values.
    # errors='coerce: any value that cannot be converted to the target format is replaced with NaN (Not a Number).
    
    # Converting 'AverageTemperature' to numeric
    data['AverageTemperature'] = pd.to_numeric(data['AverageTemperature'], errors='coerce')
    
    # Dropping rows where 'AverageTemperature' or 'Year' is NaN
    data.dropna(subset=['AverageTemperature', 'Year'], inplace=True) #inplace=True: The operation is performed directly on the original object, and no new object is created.
    
    # Applying the conversion function to latitude and longitude
    data['Latitude'] = data['Latitude'].apply(convert_to_float)
    data['Longitude'] = data['Longitude'].apply(convert_to_float)
    
    return data