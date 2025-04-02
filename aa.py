import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import os
from datetime import datetime, timezone

# Function to log the current timestamp
def log_run_time():
    with open(r"C:\Users\shijzhao\Dropbox\run_log.txt", "a") as log_file:
        log_file.write(f"Script run at: {datetime.now().isoformat()}\n")

# Call the log function at the beginning of your script
log_run_time()

# URL of the website you want to scrape
url = 'https://inews.hket.com/sran001/%E5%85%A8%E9%83%A8?mtc=20080'
atom_file = r'C:\Users\shijzhao\Dropbox\hket_feed.xml'

# Fetch the existing feed (if it exists)
existing_links = set()
if os.path.exists(atom_file):
    with open(atom_file, 'r', encoding='utf-8') as f:
        existing_feed = f.read()
        existing_links = set(existing_feed.split('<id>')[1:])

# Set headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fetch the webpage
response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Create an Atom feed
    fg = FeedGenerator()
    fg.id(url)
    fg.title('HKET News Feed')
    fg.link(href=url)
    fg.subtitle('Latest news articles from HKET.')
    fg.updated()

    # Extract articles
    for article in soup.find_all('div', class_='listing-content-container'):
        title_element = article.find('div', class_='listing-title').find('a')
        if title_element:
            title = title_element.get_text(strip=True)
            link = title_element['href']  # Get the link from the <a> tag
            content = title  # Use the title as the content if no separate content is available

            # Check for full URL if the link is relative
            if not link.startswith('http'):
                link = 'https://inews.hket.com' + link

            # Extract publication time
            formatted_time = None  # Initialize formatted_time
            date_container = article.find('div', class_='listing-information')
            if date_container:
                date_element = date_container.find('div', class_='listing-date')
                if date_element:
                    span_element = date_element.find('span', class_='font-en')  # Class name for the time
                    if span_element:
                        time_str = span_element.get_text(strip=True)  # Get the time as a string
                        now = datetime.now(timezone.utc)  # Current time in UTC
                        published_time = datetime.strptime(time_str, '%H:%M').replace(
                            year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc
                        )
                        formatted_time = published_time  # Keep it as a datetime object

            # Create an entry in the feed
            if link not in existing_links:
                entry = fg.add_entry()
                entry.id(link)
                entry.title(title)
                if formatted_time:
                    entry.updated(formatted_time)  # Use the timezone-aware datetime
                entry.content(content)  # Add content
                entry.link(href=link)

    # Output the Atom feed to a file
    atom_feed = fg.atom_str(pretty=True)  # Generate Atom feed string
    with open(atom_file, 'wb') as f:  # Open in binary mode
        f.write(atom_feed)  # Write bytes directly

    # Check if the file was created successfully
#    if os.path.exists(atom_file):
#        print(f"{atom_file} created successfully!")

#else:
#    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")