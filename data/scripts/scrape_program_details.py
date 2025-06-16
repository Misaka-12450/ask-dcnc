import csv

import requests
import re
from bs4 import BeautifulSoup

from ask_dcnc_data import get_db


def fetch_urls( ):
    conn = get_db( )
    try:
        with conn.cursor( ) as cursor:
            cursor.execute( "select url from program" )
            rows = cursor.fetchall( )
            return [ row[ 0 ] for row in rows ]
    finally:
        conn.close( )


def fetch_program_details( url: str ):
    # Get webpage
    html = requests.get( url, timeout = 10 )
    html.raise_for_status( )

    soup = BeautifulSoup( markup = html.text, features = "html.parser" )

    sections = [ ]

    for tag in soup.find_all( class_ = "rmit-bs" ):
        sections.append( tag )
    return sections


if __name__ == "__main__":
    urls = fetch_urls( )

    with open( "../raw_data/programs.csv", "w", newline = "", encoding = "utf-8" ) as f:
        write = csv.writer( f, quoting = csv.QUOTE_ALL )
        write.writerow( [ "url", "html" ] )

        for url in urls:
            # Get the HTML
            try:
                html = fetch_program_details( url )
                html_str = "".join( str( tag ) for tag in html )
                print( f"Fetched {url}" )
                write.writerow( [ url, html_str ] )

            except requests.HTTPError as e:
                print( f"HTTP error: {e} for {url}" )
            except requests.RequestException as e:
                print( f"Request failed: {e} for {url}" )
