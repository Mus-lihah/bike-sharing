import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar

# Load data
@st.cache_data
def load_data():
    df_day = pd.read_csv('day.csv')
    df_hour = pd.read_csv('hour.csv')
    return df_day, df_hour

df_day, df_hour = load_data()
for df in [df_day, df_hour]:
    df.drop(['instant', 'windspeed', 'temp', 'atemp', 'hum'], axis=1, inplace=True)
df_day.rename(columns={'dteday': 'date', 'yr': 'year', 'mnth': 'month', 'cnt': 'count'}, inplace=True)
df_hour.rename(columns={'dteday': 'date', 'yr': 'year', 'mnth': 'month', 'hr': 'hour', 'cnt': 'count'}, inplace=True)
for df in [df_day, df_hour]:
   df['date'] = pd.to_datetime(df['date'])


# Sidebar
st.sidebar.title('Choose Date Range')
min_date = min(min(df_day['date']), min(df_hour['date']))
max_date = max(max(df_day['date']), max(df_hour['date']))
start_date = st.sidebar.date_input('Start Date', min_date, min_date, max_date)
end_date = st.sidebar.date_input('End Date', max_date, min_date, max_date)

# Konversi start_date dan end_date ke dalam objek datetime64[ns]
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data based on selected date range
df_day_filtered = df_day[(df_day['date'] >= start_date) & (df_day['date'] <= end_date)]
df_hour_filtered = df_hour[df_hour['date'] == start_date]



# Title
st.title('Bike Sharing Dashboard')

# User Statistics
st.header('User Statistics')
registered_users = df_day_filtered['registered'].sum()
casual_users = df_day_filtered['casual'].sum()
total_users = registered_users + casual_users
st.write(f"Registered Users: {registered_users}")
st.write(f"Casual Users: {casual_users}")
st.write(f"Total Users: {total_users}")

# Montly Rentals
st.header('Montly Rentals')
total_bike_usage_per_month = df_day_filtered.groupby(['year', 'month'])['count'].sum().unstack()

plt.figure(figsize=(12, 6))
for year in total_bike_usage_per_month.index:
    plt.plot(total_bike_usage_per_month.columns, total_bike_usage_per_month.loc[year], marker='o', label=str(year))

plt.xlabel('Month')
plt.ylabel('Total Bike Usage')
plt.title('Total Bike Usage per Month')
plt.xticks(range(1, 13), calendar.month_name[1:13], rotation=45)
plt.legend()
plt.tight_layout()
st.pyplot(plt)

# Hour Rentals
st.header('Hourly Rentals')
hourly_bike_rentals = df_hour_filtered.groupby('hour')['count'].sum()

plt.figure(figsize=(12, 6))
plt.plot(hourly_bike_rentals.index, hourly_bike_rentals.values, marker='o', color='skyblue', linewidth=2)
plt.xlabel('Hour')
plt.ylabel('Total Bike Rentals')
plt.title('Total Bike Rentals per Hour')
plt.xticks(range(24))
plt.grid(True)
st.pyplot(plt)

# Type Day Rentals
st.header('Type Day Rentals')
grouped_by_weekday = df_day_filtered.groupby('weekday').agg({'count': 'mean'}).reset_index()
grouped_by_workingday = df_day_filtered.groupby('workingday').agg({'count': 'mean'}).reset_index()
grouped_by_holiday = df_day_filtered.groupby('holiday').agg({'count': 'mean'}).reset_index()

fig, axes = plt.subplots(3, 1, figsize=(8, 18))

# Weekday Rentals
grouped_by_weekday.index = grouped_by_weekday.index.map({0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'})

colors = ['skyblue' if c < max(grouped_by_weekday['count']) else 'orange' for c in grouped_by_weekday['count']]

axes[0].bar(grouped_by_weekday.index, grouped_by_weekday['count'], color=colors)
axes[0].set_xlabel(None)
axes[0].set_ylabel('Average Bike Usage')
axes[0].set_title('Average Bike Usage per Weekday')

# Workingday Rentals
axes[1].bar(grouped_by_workingday['workingday'].map({0: 'Holiday/Weekend', 1: 'Workingday'}), grouped_by_workingday['count'], color='orange')
axes[1].set_xlabel(None)
axes[1].set_ylabel('Average Bike Usage')
axes[1].set_title('Average Bike Usage on Workingday vs Holiday/Weekend')

# Holiday Rentals
axes[2].bar(grouped_by_holiday['holiday'].map({0: 'Non-Holiday', 1: 'Holiday'}), grouped_by_holiday['count'], color='lightgreen')
axes[2].set_xlabel(None)
axes[2].set_ylabel('Average Bike Usage')
axes[2].set_title('Average Bike Usage on Holiday vs Non-Holiday')

st.pyplot(fig)

# Seasonly Rentals
st.header('Seasonly Rentals')
seasonal_bike_rentals = df_day_filtered.groupby('season')[['registered', 'casual']].sum().reset_index()

seasons = ['Spring', 'Summer', 'Fall', 'Winter']
plt.figure(figsize=(10, 5))
plt.bar(seasonal_bike_rentals['season'], seasonal_bike_rentals['registered'], label='Registered', color='orange')
plt.bar(seasonal_bike_rentals['season'], seasonal_bike_rentals['casual'], label='Casual', color='skyblue')
plt.xlabel('Season')
plt.ylabel('Total Bike Rentals')
plt.title('Total Bike Rentals per Season')
plt.xticks(seasonal_bike_rentals['season'], seasons)
plt.legend()
st.pyplot(plt)

# Weather Rentals
st.header('Weather Rentals')
weather_mapping = {
    1: 'Clear/Partly Cloudy',
    2: 'Misty/Cloudy',
    3: 'Light Snow/Light Rain',
    4: 'Heavy Rain'
}
df_day_filtered['weather_desc'] = df_day_filtered['weathersit'].map(weather_mapping)

rentals_weather = df_day_filtered.groupby('weather_desc')['count'].sum().reset_index()

plt.figure(figsize=(8, 6))
plt.pie(rentals_weather['count'], labels=rentals_weather['weather_desc'], autopct='%1.1f%%', colors=['skyblue', 'orange', 'lightpink', 'red'])
st.pyplot(plt)

st.caption('Copyright (c) Muslihah 2024')