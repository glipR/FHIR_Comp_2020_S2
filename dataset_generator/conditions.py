import requests
import json
import os
from pathlib import Path
import shutil
import random
import math


def generate_conditions(
    condition_list,
    max_number_conditions,
    api_url,
    api_token,
    generated_conditions,
    directory_path,
):
    print("=== Generating Conditions")
    for key, display, count, medications in condition_list:
        generated_conditions[key] = []
        items = []
        items_left = max_number_conditions
        page_token = None

        while items_left > 0:
            request_url = api_url + "Condition?code={}&_count={}&apikey={}".format(
                key, min(1000, items_left), api_token
            )
            if page_token is not None:
                request_url += "&_page_token=" + page_token

            print("Requesting ", request_url, items_left, "remaining.")
            result = requests.get(request_url)
            print("Request made.")

            try:
                items += json.loads(result.text)["entry"]
                items_left -= 1000
                all_links = json.loads(result.text)["link"]
            except KeyError:
                # Request has timed out
                print("Request timed out.")
                continue

            next_link = None
            for link in all_links:
                if link["relation"] == "next":
                    next_link = link
                    break
            if next_link is None and items_left > 0:
                print("Oh no")
                break

            if items_left > 0:
                page_token = next_link["url"].split("_page_token=")[1].split("&")[0]

        print("Fetched {} {} conditions".format(len(items), display))

        items_offset = 0
        organizations = list(
            filter(
                lambda x: os.path.isdir(os.path.join(directory_path, x)),
                os.listdir(directory_path),
            )
        )
        for organization in organizations:
            org_path = os.path.join(directory_path, organization)
            pracs = list(
                filter(
                    lambda x: os.path.isdir(os.path.join(org_path, x)),
                    os.listdir(org_path),
                )
            )
            for prac in pracs:
                prac_path = os.path.join(org_path, prac)
                patients = list(
                    filter(
                        lambda x: os.path.isdir(os.path.join(prac_path, x)),
                        os.listdir(prac_path),
                    )
                )
                for pat in patients:
                    pat_path = os.path.join(prac_path, pat)
                    encounters = list(
                        filter(
                            lambda x: os.path.isdir(os.path.join(pat_path, x)),
                            os.listdir(pat_path),
                        )
                    )
                    for encounter in encounters:
                        expected_items = math.floor(
                            random.random() * (count[1] - count[0]) + count[0]
                        )

                        for entry in items[
                            items_offset : items_offset + expected_items
                        ]:
                            try:
                                # Set patient
                                entry["resource"]["subject"][
                                    "reference"
                                ] = "urn:uuid:" + pat.replace("patient", "")
                                # Set encounter
                                entry["resource"]["encounter"][
                                    "reference"
                                ] = "urn:uuid:" + encounter.replace("encounter", "")
                            except KeyError:
                                entry["resource"]["context"][
                                    "reference"
                                ] = "Encounter/" + encounter.replace("encounter", "")
                            path = Path(
                                directory_path,
                                organization,
                                prac,
                                pat,
                                encounter,
                                "condition{}".format(entry["resource"]["id"]),
                            )

                            if path.exists() and path.is_dir():
                                shutil.rmtree(path)
                            os.mkdir(path)

                            file_path = os.path.join(
                                path, "condition{}.json".format(entry["resource"]["id"])
                            )
                            generated_conditions[key].append(
                                "condition{}".format(entry["resource"]["id"])
                            )
                            del entry["search"]
                            with open(file_path, "w") as f:
                                f.write(json.dumps(entry, indent=2))
                        items_offset += expected_items

    print("Done.")
