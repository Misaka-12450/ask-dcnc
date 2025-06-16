import os
import time
import csv
import requests
from bs4 import BeautifulSoup

INPUT_CSV = '../raw_data/valid_courses.csv'
OUTPUT_CSV = '../raw_data/valid_courses_complete.csv'
DELAY = 0.001

if __name__ == '__main__':
    ids = []
    with open(INPUT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            ids.append(int(row[0]))

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(['course_id', 'url', 'title', 'body_html'])

        for i in ids:
            course_id = f"{i:06d}"
            url = f"http://www1.rmit.edu.au/courses/{course_id}"
            try:
                resp = requests.get(url, timeout=10)
            except requests.RequestException as e:
                print(e)
                continue

            if resp.status_code != 200:
                print(f"{course_id} is invalid")
            else:
                soup = BeautifulSoup(resp.text, 'html.parser')
                title = soup.title.string.strip()
                div = soup.find('div', class_='contentArea')
                body = div.decode_contents() if div else ''
                writer.writerow([course_id, url, title, body])
                print(f"Found {course_id} {title}")

            time.sleep(DELAY)
