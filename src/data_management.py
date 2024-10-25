import pandas as pd
import os
from datetime import datetime
import re
from geopy.geocoders import Nominatim

def create_filename(new_city, new_state, distance):
    formatted_city = new_city.replace(" ", "").lower()
    formatted_state = new_state.lower()
    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{formatted_city}_{formatted_state}_{distance}_{today_date}.xlsx"
    return filename


def save_to_excel(title, description, phone_number, posted, new_city, new_state, distance):
    filename = create_filename(new_city, new_state, distance)
    new_data = {
        'Title': [title],
        'Description': [description],
        'Phone Number': [phone_number],
        'Posted': [posted]
    }
    new_df = pd.DataFrame(new_data)

    # Check if the file exists and contains the same title
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        if title in existing_df['Title'].values:
            return  # Stop if title already exists
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            startrow = writer.sheets['Sheet1'].max_row
            new_df.to_excel(writer, index=False, header=False, startrow=startrow)
    else:
        new_df.to_excel(filename, index=False)


def extract_phone_numbers(description):
    phone_pattern = r'\+?\d{1,4}[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    phone_numbers = re.findall(phone_pattern, description)
    return phone_numbers


def get_location(new_city,new_state):
    geolocator = Nominatim(user_agent="my-app")
    location = geolocator.geocode(f"{new_city}, {new_state}", timeout=None)
    if not location:
        print("City not found")
        return
    return location