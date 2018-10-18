import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
import datetime
from pytz import timezone
from collections import Counter
import itertools


fileName = input('Enter the json file name: ')
print('\n')
with open(fileName, encoding = 'utf-8') as data_file:
    data = json.load(data_file)

#this is arbitrary
sender = data["participants"][0]['name']
receiver = data["participants"][1]['name']

def makePieChart(values, people, colors, title, output):
    """
    takes the number of messages, the participants, and makes a pie chart 
    graphing the distribution of values for each person in a graph with the desired
    colors and title
    """
    plt.clf()
    total = sum(values)
    plt.pie(values, labels=people, colors=colors, autopct = lambda p : '{:.0f}'.format(p * total / 100))
    plt.title(title)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output)

def makeBarGraph(values, xlabels, ylabel, color, title, output):
    """
    takes in a list of xlabels and values and makes a bar graph of the values with the xlabels on the x-axis, ylabel on the 
    y-axis, and the desired color and title
    """
    plt.clf()
    y_pos = np.arange(len(xlabels))
    plt.bar(y_pos, values, align = 'center', alpha = 0.5, color = color)
    plt.xticks(y_pos, xlabels, fontsize = 9)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(output, bbox_inches = 'tight', dpi = 100)

messages = data["messages"]
senderTimes = []
receiverTimes = []
senderMessages = []
receiverMessages = []
combinedTimes = []
combinedMessages = []

def formatDate(time):
    """takes a json time and converts it into the format time, month, day, year"""
    date = datetime.datetime.fromtimestamp(time//1000)
    return date

def filterSpam(str, includeOthers = True):
    if includeOthers:
        return not "has played, now it's your turn!" in str
    #filter out sending gifs and photos in actual count
    else:
        return not("has played, now it's your turn!" in str or " sent a photo." in str or "sent a GIF from Tenor GIF Keyboard." in str)

def makeSeries(messages, times):
    """takes a list of messages and times and makes a pandas series for more effective
    slicing and sorting"""
    times = sorted(times)
    messages.reverse()
    index = pd.DatetimeIndex(times)
    return pd.Series(messages, index)

for item in messages:
    combinedTimes.append(formatDate(item["timestamp_ms"]))
    combinedMessages.append(item['content'])
    if item["sender_name"] == sender:
        #times are in reverse chronological order from latest to earliest
        senderTimes.append(formatDate(item["timestamp_ms"]))
        senderMessages.append(item['content'])
    elif item["sender_name"] == receiver:
        receiverTimes.append(formatDate(item["timestamp_ms"]))
        receiverMessages.append(item['content'])
        

senderData = makeSeries(senderMessages, senderTimes) 
receiverData = makeSeries(receiverMessages, receiverTimes)
combinedData = makeSeries(combinedMessages, combinedTimes)

def avgMessageLength(messageList, totalMessages):
    """takes a list of message strings and the total number of messages sent and 
    calculates the average number of words per message"""
    if len(messageList) == 0 or totalMessages == 0:
        return 0
    else:
        wordsList = list(map(lambda message: message.split(), messageList))
        return sum(map(len, wordsList))/totalMessages


senderAmount, receiverAmount = len(senderMessages), len(receiverMessages)
filteredSenderMessages, filteredReceiverMessages = list(filter(lambda message : filterSpam(message, False), senderMessages)), list(filter(lambda message : filterSpam(message, False), receiverMessages))
avgSenderLength, avgReceiverLength = avgMessageLength(filteredSenderMessages, senderAmount), avgMessageLength(filteredReceiverMessages, receiverAmount)
print('Total number of messages for ' + sender + ' is ' + str(senderAmount) + '\n')
print('Total number of messages for ' + receiver + ' is ' + str(receiverAmount) + '\n')
print('Average message length for ' + sender + ' is about ' + str(round(avgSenderLength, 2)) + ' words' + '\n')
print('Average message length for ' + receiver + ' is about ' + str(round(avgReceiverLength, 2)) + ' words' + '\n')

#change later to make the correct order
calendarMonths = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June', 'July','Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']
weekdays = ['Mon.', 'Tues.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']
hours = ['12 AM', '1 AM', '2 AM', '3AM', '4 AM', '5 AM', '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM']
totalMessagesPerMonth = [len(combinedData.loc[combinedData.index.month == month]) for month in range(1, 13)]
totalMessagesPerWeekday = [len(combinedData.loc[combinedData.index.weekday == day]) for day in range(7)]
senderMessagesPerHour = [len(senderData.loc[senderData.index.hour == hour]) for hour in range(24)]
receiverMessagesPerHour = [len(receiverData.loc[receiverData.index.hour == hour]) for hour in range(24)]
monthlyMessages = [combinedData.loc[combinedData.index.month == month] for month in range(1, 13)]
averageMessageLengths = [round(avgMessageLength(messages, len(messages)), 1) for messages in monthlyMessages]

print('Making a pie chart of message distribution...')
makePieChart([senderAmount, receiverAmount], [sender, receiver], ['orange', 'dodgerblue'], 'Distribution of messages', 'messages_piechart')

print('\nMaking a graph of total messages per month... ')
makeBarGraph(totalMessagesPerMonth, calendarMonths, 'Messages', [input('Enter the desired color: ')], 'Total Messages per Month', input('What would you like your file to be named? '))

print('\n' + 'Making a graph of total messages per weekday... ')
makeBarGraph(totalMessagesPerWeekday, weekdays, 'Messages', [input('Enter the desired color: ')], 'Total Messages per Day of the Week', input('What would you like your file to be named? '))

print('\n' + 'Making a graph of average message length over time...')
makeBarGraph(averageMessageLengths, calendarMonths, 'Average Message Length', [input('Enter the desired color: ')], 'Average Message Length Over Time', input('What would you like your file to be named? '))

print('\n' + 'Making a graph of messages per hour of the day...')
df = pd.DataFrame(np.c_[senderMessagesPerHour, receiverMessagesPerHour], index = hours)
ax = df.plot.bar() 
ax.legend([sender, receiver])
plt.title('Messages per hour of the day')
plt.savefig(input('What would you like your file to be named? '), bbox_inches = 'tight')

print('Check your folder for all graphs!')
def top10Words(data, month):
    monthMessages = data.loc[data.index.month == month]
    #want to take this [date, message] format and only get a list of the messages for that month
    messageList = [monthMessages[i] for i in range(len(monthMessages))]
    top25words = ['the', 'of', 'and', 'to', 'a', 'in', 'for', 'is', 'on', 'that', 'by', 'this', 'with', 'i', 'you', 'it', 'not', 'or', 'be', 'are', 'from', 'at', 'as', 'your', 'all']
    wordsList = list(map(lambda message: message.split(), messageList))
    flattenedList = list(itertools.chain.from_iterable(wordsList))
    lowercaseList = list(map(lambda word: word.lower(), flattenedList))
    filteredList = list(filter(lambda word: word not in top25words, lowercaseList))
    return Counter(filteredList).most_common(10)
    
