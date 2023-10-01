import sqlite3
import pandas as pd
import os
import datetime
import nltk
import matplotlib.pyplot as plt
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
df['Readable_Timestamp'] = df['Timestamp'].apply(lambda x: datetime.datetime.utcfromtimestamp(x / 10**6 - 11644473600).strftime('%Y-%m-%d %H:%M:%S %Z'))

# Save the DataFrame to a CSV file
csv_filename = 'chrome_browsing_history.csv'
df.to_csv(csv_filename, index=False)

print(f"Browsing history saved to {csv_filename}")



df['Tokenized Title'] = df['Title'].apply(lambda x: nltk.word_tokenize(x))



# Create a list of all tokens
all_tokens = [token for tokens_list in df['Tokenized Title'] for token in tokens_list]

# Create a histogram of word frequencies
word_freq = nltk.FreqDist(all_tokens)

# Plot the histogram
plt.figure(figsize=(10, 5))
word_freq.plot(20, cumulative=False)
plt.xlabel('Words')
plt.ylabel('Frequency')
plt.title('Top 20 Most Common Words')
plt.show()
import re
# Define a regular expression pattern to match alphanumeric words including "@"
pattern = re.compile(r'^[a-zA-Z0-9]+$')

# Filter out symbols and keep only alphanumeric words including "@"
df['Tokenized Title'] = df['Tokenized Title'].apply(lambda tokens: [token for token in tokens if pattern.match(token)])

# Create a list of all tokens
all_tokens = [token for tokens_list in df['Tokenized Title'] for token in tokens_list]

# Create a histogram of word frequencies
word_freq = nltk.FreqDist(all_tokens)

# Plot the histogram
plt.figure(figsize=(10, 5))
word_freq.plot(20, cumulative=False)
plt.xlabel('Words')
plt.ylabel('Frequency')
plt.title('Top 20 Most Common Alphanumeric Words (including "@")')
plt.show()



#