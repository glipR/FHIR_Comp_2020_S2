import requests
import json
import os
from pathlib import Path
import shutil
import random
import math


def generate_medications(
    condition_list,
    max_number_medications,
    api_url,
    api_token,
    generate_conditions,
    directory_path,
):
    print("=== Generating Medication")

    medications = []
    for condition_item in condition_list:
        for medication in condition_item[3]:
            medications.append(medication)

    for cond_key, cond_display, cond_count, medications in condition_list:
        for key, display, count in medications:
            items = []
            items_left = 10
            page_token = None

            while items_left > 0:
                request_url = (
                    api_url
                    + "MedicationRequest?code={}&_count={}&apikey={}".format(
                        key, 10, api_token
                    )
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

            print("Fetched {} {} medications ".format(len(items), display))

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
                            condition_path = os.path.join(pat_path, encounter)
                            conditions = list(
                                filter(
                                    lambda x: os.path.isdir(
                                        os.path.join(condition_path, x)
                                    )
                                    and x.startswith("condition"),
                                    os.listdir(condition_path),
                                )
                            )
                            for condition in conditions:
                                for cond_item in generate_conditions[cond_key]:
                                    if condition == cond_item:
                                        expected_items = math.floor(
                                            random.random() * (count[1] - count[0])
                                            + count[0]
                                        )

                                        for entry in items[
                                            items_offset : items_offset + expected_items
                                        ]:
                                            try:
                                                # Set patient
                                                entry["resource"]["subject"][
                                                    "reference"
                                                ] = "urn:uuid:" + pat.replace(
                                                    "patient", ""
                                                )
                                                # Set encounter
                                                entry["resource"]["context"][
                                                    "reference"
                                                ] = "Encounter/" + encounter.replace(
                                                    "encounter", ""
                                                )
                                                # Set reason reference
                                                entry["resource"]["reasonReference"][0][
                                                    "reference"
                                                ] = "urn:uuid:" + condition.replace(
                                                    "condition", ""
                                                )
                                                # Set practitioner
                                                entry["resource"]["requester"]["agent"][
                                                    "reference"
                                                ] = "urn:uuid:" + prac.replace(
                                                    "practitioner", ""
                                                )
                                                # Set organization
                                                entry["resource"]["requester"][
                                                    "onBehalfOf"
                                                ][
                                                    "reference"
                                                ] = "urn:uuid:" + organization.replace(
                                                    "organization", ""
                                                )
                                                # entry['resource']['encounter']['reference'] = 'urn:uuid:' + encounter.replace('encounter', '')
                                            except KeyError:
                                                raise

                                            path = Path(
                                                directory_path,
                                                organization,
                                                prac,
                                                pat,
                                                encounter,
                                                "medicationrequest{}".format(
                                                    entry["resource"]["id"]
                                                ),
                                            )

                                            if path.exists() and path.is_dir():
                                                shutil.rmtree(path)
                                            os.mkdir(path)

                                            file_path = os.path.join(
                                                path,
                                                "medicationrequest{}.json".format(
                                                    entry["resource"]["id"]
                                                ),
                                            )
                                            del entry["search"]
                                            with open(file_path, "w") as f:
                                                f.write(json.dumps(entry, indent=2))
                                        items_offset += expected_items

    print("Done.")
