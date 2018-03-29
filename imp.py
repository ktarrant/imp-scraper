import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from collections import OrderedDict

from util import guess_year

IMP_URL = "https://www.impconcerts.com/shows/"

def find_event_entries(soup):
    main = soup.find("main")
    entries = main.find_all(attrs={"class": "list-view-item"})

    for entry in entries:
        event_details, price_details = entry.find_all("div")

        dates = entry.find(attrs={"class": "dates"})
        date_list = dates.text.split("-")
        parsed_dates = [datetime.strptime(date.strip(), "%a %d %b") for date in date_list]
        years = [guess_year(date.month, date.day) for date in parsed_dates]

        headliner_summary = event_details.find(attrs={"class": "headliners summary"})
        # try to reduce excessive whitespace
        headliner_summary_text = headliner_summary.text.replace("   ", "")
        supports_description = event_details.find(attrs={"class": "supports description"})
        if supports_description:
            supports_description_text = supports_description.text
        else:
            supports_description_text = ""

        venue_location = event_details.find(attrs={"class": "venue location"})
        venue_location_text = venue_location.text

        event_times = event_details.find(attrs={"class": "times"})
        special_title = event_times.find(attrs={"class": "value-title"})
        duration_str = special_title.attrs["title"]
        date_str, time_str = duration_str.split("T")
        starttime_str = time_str.split("-")[0]
        date_p = datetime.strptime(date_str, "%Y-%m-%d")
        time_p = datetime.strptime(starttime_str, "%H:%M:%S")
        start_times = [
            datetime(year=year, month=date.month, day=date.day, hour=time_p.hour, minute=time_p.minute)
            for date, year in zip(parsed_dates, years)
        ]

        price_range = price_details.find(attrs={"class":"price-range"})
        price_range_text = price_range.text.strip()

        for start_time in start_times:
            yield OrderedDict([
                ("datetime", start_time),
                ("venue_location", venue_location_text),
                ("headliner", headliner_summary_text),
                ("supports", supports_description_text),
                ("price", price_range_text),
            ])

def load_imp_data():
    with urllib.request.urlopen(IMP_URL) as urlobj:
        soup = BeautifulSoup(urlobj.read(), "html.parser")

    df = pd.DataFrame(find_event_entries(soup))

    return df