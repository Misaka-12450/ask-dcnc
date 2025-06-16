import time
import csv
import requests
from bs4 import BeautifulSoup

start = 1000
end = 59999
delay = 0.5
output = 'valid_courses.csv'

if __name__ == '__main__':
    session = requests.Session()

    with open(output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['course_id', 'url', 'title'])

        for i in range(start, end):
            course_id = f"{i:06d}"
            url = f"http://www1.rmit.edu.au/courses/{course_id}"

            try:
                resp = session.get(url, timeout=10)
            except requests.RequestException as e:
                print(f"[ERROR] {url} → {e}")
                continue

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                title = soup.title.string.strip()
                writer.writerow([course_id, url, title])
                print(f"[FOUND] {course_id} → \"{title}\"")

            time.sleep(delay)
