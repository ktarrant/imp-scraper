import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from collections import OrderedDict

from util import guess_year

IMP_URL = "https://www.impconcerts.com/shows/"

def parse_dates(list_view_item):
    dates = list_view_item.find(attrs={"class": "dates"})
    date_list = dates.text.split("-")
    parsed_dates = [datetime.strptime(date.strip(), "%a %d %b") for date in date_list]
    years = [guess_year(date.month, date.day) for date in parsed_dates]
    return [datetime(year=year, month=d.month, day=d.day) for year, d in zip(years, parsed_dates)]

def parse_headliner(list_view_details):
    headliner_summary = list_view_details.find(attrs={"class": "headliners summary"})
    # try to reduce excessive whitespace
    headliner_summary_text = headliner_summary.text.replace("   ", "")
    return headliner_summary_text

def parse_supports(list_view_details):
    supports_description = list_view_details.find(attrs={"class": "supports description"})
    if supports_description:
        return supports_description.text
    else:
        return ""

def parse_venue(list_view_details):
    venue_location = list_view_details.find(attrs={"class": "venue location"})
    venue_location_text = venue_location.text
    return venue_location_text

def parse_time(list_view_details):
    event_times = list_view_details.find(attrs={"class": "times"})
    special_title = event_times.find(attrs={"class": "value-title"})
    duration_str = special_title.attrs["title"]
    date_str, time_str = duration_str.split("T")
    starttime_str = time_str.split("-")[0]
    date_p = datetime.strptime(date_str, "%Y-%m-%d")
    time_p = datetime.strptime(starttime_str, "%H:%M:%S")
    return datetime(year=date_p.year, month=date_p.month, day=date_p.day,
                    hour=time_p.hour, minute=time_p.minute, second=time_p.second)

def parse_price(div_ticket_price):
    soldout_tag = div_ticket_price.find("p", attrs={"class": "sold-out-tag"})
    soldout_norm = div_ticket_price.find("h3", attrs={"class": "sold-out"})
    if soldout_tag or soldout_norm:
        return "SOLD OUT"
    else:
        price_range = div_ticket_price.find("h3", attrs={"class": "price-range"}, recursive=False)
        if price_range:
            price_range_text = price_range.text.strip()
            min_price = price_range_text.split(" - ")[0]
            return min_price
        else:
            return "???"

def find_event_entries(soup):
    main = soup.find("main")
    list_view = main.find(attrs={"class": "list-view"})
    children = list_view.findChildren()

    for entry in children:
        if ("class" not in entry.attrs) or ("list-view-item" not in entry.attrs["class"]):
            continue

        event_details = entry.find("div", attrs={"class": "list-view-details"})

        price_details = entry.find("div", attrs={"class": "ticket-price"})

        event_dates = parse_dates(entry)

        headliner = parse_headliner(event_details)

        supports = parse_supports(event_details)

        venue = parse_venue(event_details)

        start_time = parse_time(event_details)

        start_times = [
            datetime(year=event_date.year, month=event_date.month, day=event_date.day,
                     hour=start_time.hour, minute=start_time.minute)
            for event_date in event_dates
        ]

        min_price = parse_price(price_details)

        for start_time in start_times:
            yield OrderedDict([
                ("datetime", start_time),
                ("venue_location", venue),
                ("min_price", min_price),
                ("headliner", headliner),
                ("supports", supports),
            ])

def load_imp_data():
    with urllib.request.urlopen(IMP_URL) as urlobj:
        soup = BeautifulSoup(urlobj.read(), "html.parser")

    df = pd.DataFrame(find_event_entries(soup))

    return df