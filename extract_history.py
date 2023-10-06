import sqlite3
import pandas as pd
import os
import datetime
import nltk
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import re

# Path to the Chrome history database (macOS)

chrome_history_db = os.path.expanduser(
    '/Users/avinashkalyani/Library/Application Support/Google/Chrome/Default/History'
)

# Establish a connection to the Chrome history database
connection = sqlite3.connect(chrome_history_db)
cursor = connection.cursor()

# SQL query to retrieve browsing history
query = "SELECT urls.url, urls.title, visits.visit_time " \
        "FROM urls INNER JOIN visits ON urls.id = visits.url ORDER BY visits.visit_time DESC"

# Execute the query
cursor.execute(query)

# Fetch all the rows into a list
history_data = cursor.fetchall()

# Close the database connection
connection.close()

# Convert the data into a DataFrame
df = pd.DataFrame(history_data, columns=['URL', 'Title', 'Timestamp'])

# Convert timestamp to a readable date and time format
df['Readable_Timestamp'] = df['Timestamp'].apply(
    lambda x: datetime.datetime.utcfromtimestamp(x / 10 ** 6 - 11644473600).strftime('%Y-%m-%d %H:%M:%S %Z'))

# Save the DataFrame to a CSV file
csv_filename = 'chrome_browsing_history.csv'
df.to_csv(csv_filename, index=False)

print(f"Browsing history saved to {csv_filename}")

# if the CSV file already exists, then import it as a df:
df = pd.read_csv(csv_filename)

# Define a regular expression pattern to match alphanumeric words
pattern = re.compile(r'^[a-zA-Z0-9@]+$')


# Define a function to tokenize titles
def tokenize_title(title):
    if isinstance(title, str):
        return word_tokenize(title.lower())
    else:
        return []


# Tokenize the 'Title' column
df['Tokenized Title'] = df['Title'].apply(lambda x: tokenize_title(x))

# Filter out symbols and keep only alphanumeric words including
df['Tokenized Title'] = df['Tokenized Title'].apply(lambda tokens: [token for token in tokens if pattern.match(token)])

# Create categories dictionary to find a match in the Tokenized title:

custom_categories = {
    "News": ["news", "headline", "press", "times"],
    "Social Media": ["facebook", "twitter", "linkedin", "instagram"],
    "Work": ["work", "office", 'github', 'stackoverflow', 'gate2', 'ovgu', 'exmail', 'dzne', "frontiersin", "model",
             'unsupervised', "linear", "ieeexplore", "papers", "scholar"],
    "Entertainment": ["movies", "music", "games", "entertainment", "netflix", "youtube"],
    "Shopping": ["amazon", "ebay", "shopping", "store", "zalando"],
    "Travel": ["booking", "hotel", "air", "flight", "db", 'toronto'],
    "Other": []  # Default category
}


# Function to categorize titles
def categorize_title(tokens):
    for category, keywords in custom_categories.items():
        if any(keyword in tokens for keyword in keywords):
            return category
    return "Other"  # Default category if none of the custom categories match


# Categorize the titles
df['Category'] = df['Tokenized Title'].apply(categorize_title)


# Function to tokenize and categorize URLs
def categorize_url(url):
    # Extract the hostname (e.g., "example.com") from the URL
    hostname = url.split('//')[1].split('/')[0].lower()

    # Tokenize the hostname
    tokens = word_tokenize(hostname)

    # Categorize based on the tokens
    for category, keywords in custom_categories.items():
        if any(keyword in tokens for keyword in keywords):
            return category
    return "Other"  # Default category if none of the custom categories match


# Categorize the URLs
df['Url_Category'] = df['URL'].apply(categorize_url)

# Print the DataFrame with categories
# Create a histogram of category frequencies
category_freq = df['Category'].value_counts()

# Plot the histogram
plt.figure(figsize=(10, 5))
category_freq.plot(kind='bar')
plt.xlabel('Category')
plt.ylabel('Frequency')
plt.title('Category Histogram')
plt.xticks(rotation=45)  # Rotate category labels for better visibility
plt.show()



#Convert 'Timestamp' column to datetime
df['Timestamp'] = pd.to_datetime(df['Readable_Timestamp'])

# Filter out 'Other' category
df = df[df['Category'] != 'Other']

# Extract the hour from the timestamp
df['Hour'] = df['Timestamp'].dt.hour

# Group by hour and category, and count occurrences
hourly_category_counts = df.groupby(['Hour', 'Category']).size().unstack(fill_value=0)

# Plot the hourly histogram
hourly_category_counts.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.xlabel('Hour of Day')
plt.ylabel('Frequency')
plt.title('Hourly Histogram of Categories (Excluding "Other")')
plt.legend(title='Category')
plt.show()