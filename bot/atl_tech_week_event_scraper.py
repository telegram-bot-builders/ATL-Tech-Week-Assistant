import requests
from bs4 import BeautifulSoup
import json

class EventScraper:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    def get_soup(self):
        response = requests.get(self.url)
        return BeautifulSoup(response.text, 'html.parser')

    def extract_event_details(self, event_item):
        event = {}
        event_link = event_item.select_one('.events_item-link')
        if event_link:
            event['details_link'] = event_link['href']
        
        event_title = event_item.select_one('.heading-style-h5')
        if event_title:
            event['title'] = event_title.text.strip()
        
        event_venue = event_item.select_one('.heading-style-h6')
        if event_venue:
            event['venue'] = event_venue.text.strip()
        
        event_description = event_item.select_one('.text-block-7')
        if event_description:
            event['description'] = event_description.text.strip()
        
        event_date = event_item.select_one('.events_date-wrapper .text-size-small')
        if event_date:
            event['date'] = event_date.text.strip()
        
        event_time = event_item.select('.events_date-wrapper .text-size-small')
        if len(event_time) > 1:
            event['start_time'] = event_time[1].text.strip()
            event['end_time'] = event_time[2].text.strip()
        
        return event

    def scrape_events(self):
        events = []
        for event_item in self.soup.select('.collection-item-2'):
            event = self.extract_event_details(event_item)
            events.append(event)
        return events

    def fetch_event_details(self, event):
        details_url = f"https://atl.tech{event['details_link']}"
        response = requests.get(details_url)
        details_soup = BeautifulSoup(response.text, 'html.parser')

        about_section = details_soup.select_one('.event-desc')
        if about_section:
            event['event_details'] = about_section.text.strip()
        
        return event

    def update_events_with_details(self, events):
        updated_events = []
        for event in events:
            updated_event = self.fetch_event_details(event)
            updated_events.append(updated_event)
        return updated_events

    def save_to_json(self, events, filename):
        with open(filename, 'w') as f:
            json.dump(events, f, indent=4)
        print(f"Events saved to {filename}")


def main():
    url = 'https://www.atl.tech/events'
    scraper = EventScraper(url)
    events = scraper.scrape_events()
    updated_events = scraper.update_events_with_details(events)
    scraper.save_to_json(updated_events, 'atl_tech_week_events.json')


if __name__ == "__main__":
    main()

