import requests
import json
import os
from pathlib import Path
import shutil
import random
import math


def generate_observations(
    observation_list, total_encounters, api_url, api_token, directory_path
):
    print("=== Generating Observations")
    for key, display, count, extra_info in observation_list:
        obs = []
        # A safe estimate of how many observations will be needed.
        obs_left = int(total_encounters * (count[0] + 0.66 * (count[1] - count[0])))
        page_token = None

        while obs_left > 0:
            request_url = (
                api_url
                + "Observation?code=http://loinc.org|{}&_count={}&apikey={}".format(
                    key, min(1000, obs_left), api_token
                )
            )
            if page_token is not None:
                request_url += "&_page_token=" + page_token

            print("Requesting ", request_url, obs_left, "remaining.")
            result = requests.get(request_url)
            print("Request made.")

            obj = json.loads(result.text)

            try:
                obs += obj["entry"]
                obs_left -= 1000
                all_links = obj["link"]
            except KeyError:
                # Request has timed out
                print("Request timed out.")
                continue

            next_link = None
            for link in all_links:
                if link["relation"] == "next":
                    next_link = link
                    break
            if next_link is None and obs_left > 0:
                print("Oh no")
                break

            if obs_left > 0:
                page_token = next_link["url"].split("_page_token=")[1].split("&")[0]

        print("Fetched {} {} observations".format(len(obs), display))

        obs_offset = 0
        all_orgs = os.path.join(directory_path, "organizations")
        organizations = list(
            filter(
                lambda x: os.path.isdir(os.path.join(all_orgs, x)), os.listdir(all_orgs)
            )
        )
        for organization in organizations:
            org_path = os.path.join(all_orgs, organization)
            all_patients = os.path.join(org_path, "patients")
            patients = list(
                filter(
                    lambda x: os.path.isdir(os.path.join(all_patients, x)),
                    os.listdir(all_patients),
                )
            )
            for patient in patients:
                pat_path = os.path.join(all_patients, patient)
                all_encounters = os.path.join(pat_path, "encounters")
                encounters = list(
                    filter(
                        lambda x: os.path.isdir(os.path.join(all_encounters, x)),
                        os.listdir(all_encounters),
                    )
                )
                for encounter in encounters:
                    expected_obs = math.floor(
                        random.random() * (count[1] - count[0]) + count[0]
                    )

                    for index, entry in enumerate(
                        obs[obs_offset : obs_offset + expected_obs], start=obs_offset
                    ):
                        if "value_generator" in extra_info:
                            entry["resource"]["valueQuantity"]["value"] = extra_info[
                                "value_generator"
                            ](index)
                        try:
                            # Set patient
                            entry["resource"]["subject"][
                                "reference"
                            ] = "urn:uuid:" + patient.replace("patient", "")
                            # Set encounter
                            entry["resource"]["encounter"][
                                "reference"
                            ] = "urn:uuid:" + encounter.replace("encounter", "")
                        except KeyError:
                            entry["resource"]["context"][
                                "reference"
                            ] = "Encounter/" + encounter.replace("encounter", "")
                        path = Path(
                            all_encounters,
                            encounter,
                            "observations",
                            "observation{}.json".format(entry["resource"]["id"]),
                        )

                        del entry["search"]
                        with open(path, "w") as f:
                            f.write(json.dumps(entry, indent=2))
                    obs_offset += expected_obs

    print("Done.")
