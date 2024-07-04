import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import tkinter as tk
from tkinter import ttk
import seaborn as sns

data = pd.read_csv('hotel_booking.csv') #vazw to hotel bookings csv divazondas to me th pandas se ena dataframe "data"

def get_season(month): #sinartisi gia na pairnoume apo to dataframe me morfh integers ta months [1-12] kai na ta katatasoume se seasons
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'

data['season'] = data['arrival_date_month'].apply(lambda x: get_season(pd.to_datetime(x, format='%B').month)) #to apply einai san to map pou mathame
#ftiaxnei sto processed csv ena column "season" sto opoio kanei apply sto arivale_date_month tou dataframe th lambda function pou gia kathe month(x sto λ func) to kanei datetime antikeimeno ths pandas
#attempt at using lambda func instead of all this ^^:
#  def month_name_to_season(month_name):
#   month_number = pd.to_datetime(month_name, format='%B').month
#   return get_season(month_number)
#data['season'] = data['arrival_date_month'].apply(month_name_to_season)

data['reservation_status_date'] = pd.to_datetime(data['reservation_status_date']) #convert to reservation_status_date column se datetime format

mean_stays = data.groupby('hotel')[['stays_in_weekend_nights', 'stays_in_week_nights']].mean() #average apo stays_in_weekend_nights kai stays_in_week_nights grouped ana hotel
mean_stays['total_stays'] = mean_stays['stays_in_weekend_nights'] + mean_stays['stays_in_week_nights'] #total stays ara to sum apo ta week kai weekend stays

cancelled_ratio = data.groupby('hotel')['is_canceled'].mean() #average cancel ratio ana hotel

monthly_bookings = data.groupby(['hotel', 'arrival_date_month']).size().unstack() #opws h fold h to reduce step sto mapreduce, h .size() mazeuei ta occurances twn stoixeiwn se enan arithmo kai h unfold ta omadopoiei conveniently

seasonal_bookings = data.groupby(['hotel', 'season']).size().unstack() #gia kathe combination twn columns hotel kai season poy egine me to groupby opws kai panw, metra ta occurances

seasonal_cancellations = data[data['is_canceled'] == 1].groupby(['hotel', 'season']).size().unstack()

room_type_bookings = data.groupby(['hotel', 'reserved_room_type']).size().unstack()

#typos pelath
def get_customer_type(row):
    if row['adults'] > 0 and (row['children'] > 0 or row['babies'] > 0):
        return 'Family'
    elif row['adults'] == 2 and (row['children'] == 0 or row['babies'] == 0):
        return 'Couple'
    elif row['adults'] > 2 and (row['children'] == 0 or row['babies'] == 0):
        return 'Group'
    else:
        return 'Solo'

data['customer_type'] = data.apply(get_customer_type, axis=1) #krata ton typo ton pelatwn analoga to posa kai poia atoma einai
customer_type_counts = data.groupby(['hotel', 'customer_type']).size().unstack()

time_trends = data.groupby(['reservation_status_date', 'hotel']).size().unstack()

# syndesh se SQLite DATABASE alla xwris cursor gia query giati einai mono gia apothikeush opws leei h ekfwnhsh ---------------------------------------------------------------
conn = sqlite3.connect('hotel_bookings.db')
data.to_sql('bookings', conn, if_exists='replace', index=False) #me th xrhsh ths .to_sql ta dedomena apto dataframe pou douleya tosh wra grafontai ste pinaka stoixismena mesa sto DB, schema einai to default h main

data.to_csv('processed_hotel_bookings.csv', index=False) #to processed arxeio twn apotelesmatwn


#menu epilopges PLOTS --------------------------------------------------------------------------------------------------------------------------------------------------------
def show_mean_stays():
    fig, ax = plt.subplots(figsize=(6.4, 12))  # ftiaxnei to diagramma gia ta average stays, allaksa to default size gia na fainetai kathara olo
    mean_stays.plot(kind='bar', stacked=True, ax=ax) #edw anagastika na ftiaksw subplot pou perna ws parametros sto plot
    ax.set_title('Average Stays')
    plt.xlabel('Stays')
    plt.show()

def show_cancelled_ratio():
    fig, ax = plt.subplots(figsize=(6.4, 12)) #diagramma gia cancelled ratio
    cancelled_ratio.plot(kind='bar', ax=ax)
    ax.set_title('Cancelled Ratio')
    plt.xlabel('Ratio')
    plt.show()

def show_monthly_bookings():
    monthly_bookings.plot(kind='bar', stacked=True, figsize=(6.4, 12))   #diagramma gia mhniaies krathseis
    plt.title('Monthly Bookings')
    plt.xlabel('Bookings')
    plt.show()

# def show_seasonal_bookings(): **palio blotbar pou den evgaze ksexwrista gia resort kai city hotel**
#     # fig, ax = plt.subplots(figsize=(6.4, 12)) #diagramma gia tis krathseis ana epoxh
#     # sns.barplot(data=seasonal_bookings, ax=ax, label='Seasonal')
#     # ax.set_xlabel('Seasons')
#     # plt.show()
#     seasonal_bookings.plot(kind='bar', stacked=True, figsize=(6.4, 12))  # diagramma gia mhniaies krathseis
#     plt.title('seasonal Bookings')
#     plt.xlabel('Bookings')
#     plt.show()

def show_seasonal_bookings(): #diagramma gia  seasonal bookings
    #Reset to index gia na ta emfanizei se 2 sthles, hotel kai season
    seasonal_bookings_reset = seasonal_bookings.reset_index()

    #Melt to DataFrame se long format gia easy plotting me seaborn
    seasonal_bookings_melted = seasonal_bookings_reset.melt(id_vars=['hotel'], var_name='season', value_name='bookings')

    plt.figure(figsize=(10, 6))
    sns.barplot(data=seasonal_bookings_melted, x='season', y='bookings', hue='hotel')
    plt.title('Seasonal Bookings by Hotel')
    plt.xlabel('Season')
    plt.ylabel('Number of Bookings')
    plt.legend(title='Hotel')
    plt.show()

def show_seasonal_cancellations(): # gia seasonal cancellations
    seasonal_cancellations_reset = seasonal_cancellations.reset_index()

    seasonal_cancellations_melted = seasonal_cancellations_reset.melt(id_vars=['hotel'], var_name='season', value_name='cancellations')

    plt.figure(figsize=(10, 6))
    sns.barplot(data=seasonal_cancellations_melted, x='season', y='cancellations', hue='hotel')
    plt.title('Seasonal Cancellations by Hotel')
    plt.xlabel('Season')
    plt.ylabel('Number of Cancellations')
    plt.legend(title='Hotel')
    plt.show()


def show_room_type_bookings():
    room_type_bookings.plot(kind='bar', stacked=True, figsize=(6.4, 12)) #diagramma gia typo domatiou
    plt.title('Room Type Bookings')
    plt.xlabel('Bookings')
    plt.show()

# def show_customer_type_counts(): **palio version me morfh bar kai oxi pie chart**
#     customer_type_counts.plot(kind='bar', stacked=True, figsize=(6.4, 12)) #diagramma gia to posoi apto kathe eidous customer yparxoun
#     plt.title('Customer Type Counts')
#     plt.xlabel('Counts')
#     plt.show()
def show_customer_type_counts():
    colors = ['#800080', '#66b3ff', '#99ff99', '#00c04b']

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    fig.suptitle('Customer Type Distribution by Hotel', fontsize=16)

    #pie chart gia kathe hotel
    for ax, (hotel, counts) in zip(axes, customer_type_counts.iterrows()):
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.set_title(f'{hotel} Hotel')

    plt.show()


def show_time_trends():
    time_trends.plot(figsize=(6.4, 6)) #diagramma gia tis tashs krathsewn
    plt.title('Time Trends')
    plt.xlabel('Time')
    plt.ylabel('Bookings')
    plt.show()

# creating the GUI -----------------------------------------------------------------------------------------------------------------------------------------------
window = tk.Tk() #ftaxnoume to parathiro tou gui
window.title("Hotel Booking Analysis")
menu = ttk.Notebook(window)

tabs = ["Mean Stays", "Cancelled Ratio", "Monthly Bookings", "Seasonal Bookings", "Seasonal Cancellations", "Room Type Bookings", "Customer Type Bookings", "Time Trends"]
commands = [show_mean_stays, show_cancelled_ratio, show_monthly_bookings, show_seasonal_bookings, show_seasonal_cancellations, show_room_type_bookings, show_customer_type_counts, show_time_trends]

for tab_name, command in zip(tabs, commands):
    tab = ttk.Frame(menu)
    menu.add(tab, text=tab_name)

    btn = tk.Button(tab, text=f"Show {tab_name}", command=command,  bg='LightSteelBlue2', fg='gray25', font=('Helvetica', 12, 'bold'))
    btn.pack()

menu.pack(expand=True, fill="both")

window.mainloop()

