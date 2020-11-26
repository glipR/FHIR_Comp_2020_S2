what_to_count = "Practitioner"
base_url = str(
    "https://syntheticmass.mitre.org/v1/fhir/{}}?_count=1000&apikey=b6ai0PI8aEEGrUGnMA18zAZsfqaBbFdD".format(
        what_to_count
    )
)


import requests
import json

count = 0
page_token = None
while True:
    url = (
        base_url + "&_page_token=" + page_token if page_token is not None else base_url
    )
    print("Making request to ", url)
    result = requests.get(url)
    request_failed = False
    try:
        links = json.loads(result.text)["link"]
    except KeyError:
        print(result.text)
        request_failed = True
    next_link = list(filter(lambda x: x["relation"] == "next", links))
    if len(next_link) > 0:
        count += 1000
        page_token = next_link[0]["url"].split("_page_token=")[1]
    if not request_failed and len(next_link) == 0:
        print(count)
        break
    print("Request finished")
