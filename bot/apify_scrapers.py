from dotenv import load_dotenv
import os, json, pprint
from apify_client import ApifyClient

load_dotenv()

# Initialize the ApifyClient with your API token
client = ApifyClient(os.getenv('APIFY_API_TOKEN'))


def scrape_linkedin_profile(url):
    # Prepare the Actor input
    run_input = {
        "startUrls": [{
            "url": url,
            "id": "1",
        }]
    }

    # Run the Actor and wait for it to finish
    run = client.actor("AgfKk0sQQxkpQJ1Dt").call(run_input=run_input)

    if run["status"] == "SUCCEEDED":
        print("Actor run succeeded!")

    # Fetch and return Actor results from the run's dataset (if there are any)
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)

    return results[0]


if __name__ == '__main__':
    # Scrape a LinkedIn profile
    url = "https://www.linkedin.com/in/nathan-baker-116b49310/"
    results = scrape_linkedin_profile(url)
    pprint.pprint(results)