import xml.etree.ElementTree as ET
import re

tree = ET.parse('sitemap.xml')
root = tree.getroot()

namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

with open("program_urls.txt", "a") as f:
    for url in root.findall('ns:url', namespace):
        loc = url.find('ns:loc', namespace)
        if loc is not None:
            if re.search(r'/levels-of-study/(undergraduate-study|postgraduate-study|research-programs)/.*(auscy|ausbr|ausbu)$'
                    , loc.text):
                f.write(loc.text + '\n')
