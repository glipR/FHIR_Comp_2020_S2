import collections
import requests
import json
import os
import random
import math
from .randomisation import RandomGenerator


def generate_practitioners(number_practitioners, orgs_per_prac, api_url, api_token, directory_path):
    """
    :param number_practitioners: Maximum number of practitioners in total
    :param directory_path: Directory containing all of the organizations
    """
    print("=== Generating practitioners")
    practitioners = []
    pracs_left = number_practitioners
    page_token = None
    while pracs_left > 0:
        request_url = api_url + "Practitioner?_count={}&apikey={}".format(
            min(1000, pracs_left), api_token
        )
        if page_token is not None:
            request_url += "&_page_token=" + page_token

        print("Requesting ", request_url)
        result = requests.get(request_url)
        print("Request made.")

        try:
            practitioners += json.loads(result.text)["entry"]
            pracs_left -= 1000
            all_links = json.loads(result.text)["link"]
        except KeyError:
            # Request has timed out
            continue

        next_link = None
        for link in all_links:
            if link["relation"] == "next":
                next_link = link
                break

        if next_link is None and pracs_left > 0:
            print("Oh no")
            break

        if pracs_left > 0:
            page_token = next_link["url"].split("_page_token=")[1]

    print("Got {} practitioners".format(len(practitioners)))

    from collections import defaultdict

    org_mapping = defaultdict(list)

    # We need to first ensure that every organization has a practitioner. Then we can randomise.

    prac_ids = [practitioner["resource"]["id"] for practitioner in practitioners]

    prac_to_orgs = collections.defaultdict(set)
    for i, practitioner in enumerate(prac_ids[:len(RandomGenerator.ALL_ORGS)]):
        prac_to_orgs[practitioner].add(RandomGenerator.ALL_ORGS[i])

    for practitioner in prac_ids:
        n_orgs = math.floor(random.random() * (orgs_per_prac[1] - orgs_per_prac[0])) + orgs_per_prac[0]
        for _ in range(n_orgs):
            prac_to_orgs[practitioner].add(RandomGenerator.random_org())
    
    for practitioner in practitioners:
        del practitioner["search"]
        for org in prac_to_orgs[practitioner["resource"]["id"]]:
            prac_path = os.path.join(
                directory_path, "organizations/organization{}".format(org), "practitioners"
            )
            filename = "practitioner{}.json".format(practitioner["resource"]["id"])
            org_mapping[org].append(practitioner["resource"]["id"])
            with open(os.path.join(prac_path, filename), "w") as f:
                f.write(json.dumps(practitioner, indent=2))

    all_pracs = os.path.join(directory_path, "all_practitioners")
    for i, prac in enumerate(practitioners):
        prac_file = os.path.join(
            all_pracs, "practitioner{}.json".format(prac["resource"]["id"])
        )
        with open(prac_file, "w") as f:
            f.write(json.dumps(prac, indent=2))

    print("Done.")
    return org_mapping
