import requests
import json
import os
import shutil
import random
import math
from pathlib import Path
from dataset_generator.randomisation import RandomGenerator


def generate_encounters(
    count,
    max_number_encounters,
    pracs_per_encounter,
    api_url,
    api_token,
    directory_path,
):
    print("=== Generating Encounters")
    encounters = []
    enc_left = max_number_encounters
    page_token = None

    while enc_left > 0:
        request_url = api_url + "Encounter?_count={}&apikey={}".format(
            min(1000, enc_left), api_token
        )
        if page_token is not None:
            request_url += "&_page_token=" + page_token

        print("Requesting ", request_url, enc_left, "remaining.")
        result = requests.get(request_url)
        print("Request made.")

        obj = json.loads(result.text)

        try:
            encounters += obj["entry"]
            enc_left -= 1000
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
        if next_link is None and enc_left > 0:
            print("Oh no")
            break

        if enc_left > 0:
            page_token = next_link["url"].split("_page_token=")[1]

    print("Fetched {} encounters".format(len(encounters)))

    enc_offset = 0
    org_path = os.path.join(directory_path, "organizations")
    organizations = list(
        filter(lambda x: os.path.isdir(os.path.join(org_path, x)), os.listdir(org_path))
    )
    for organization in organizations:
        spec_org_path = os.path.join(org_path, organization)
        pat_path = os.path.join(spec_org_path, "patients")
        patients = list(os.listdir(pat_path))
        for pat in patients:
            expected_enc = math.floor(
                random.random() * (count[1] - count[0]) + count[0]
            )

            with open(os.path.join(pat_path, pat, f"{pat}.json"), "r") as f:
                patient_data = json.load(f)
                prac_list = [
                    info["reference"][9:]
                    for info in patient_data["resource"]["generalPractitioner"]
                ]
                prac_data = []
                for prac in prac_list:
                    with open(
                        os.path.join(
                            spec_org_path,
                            "practitioners",
                            "practitioner{}".format(prac),
                        ),
                        "r",
                    ) as f:
                        prac_data.append(json.load(f))

            for entry in encounters[enc_offset : enc_offset + expected_enc]:
                # Set patient
                entry["resource"]["subject"]["reference"] = "urn:uuid:" + pat.replace(
                    "patient", ""
                )
                # Set practitioners
                n_pracs = math.floor(
                    random.random() * (pracs_per_encounter[1] - pracs_per_encounter[0])
                    + pracs_per_encounter[0]
                )
                prac_set = set(
                    [
                        RandomGenerator.random_select(
                            range(len(prac_list)), RandomGenerator.FRONT_BIAS_PRACS
                        )
                        for _ in range(n_pracs)
                    ]
                )
                entry["resource"]["participant"] = [
                    {
                        "individual": {
                            "reference": "urn:uuid:"
                            + prac_data[prac]["resource"]["id"],
                            "display": prac_data[prac]["resource"]["name"][0]["prefix"][
                                0
                            ]
                            + " "
                            + prac_data[prac]["resource"]["name"][0]["given"][0]
                            + " "
                            + prac_data[prac]["resource"]["name"][0]["family"],
                        }
                    }
                    for prac in prac_set
                ]
                # Set organization
                entry["resource"]["serviceProvider"][
                    "reference"
                ] = "urn:uuid:" + organization.replace("organization", "")
                # Set type of encounter
                entry["type"] = [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "162673000",
                                "display": "General examination of patient (procedure)",
                            }
                        ],
                        "text": "General examination of patient (procedure)",
                    }
                ]

                path = Path(
                    directory_path,
                    "organizations",
                    organization,
                    "patients",
                    pat,
                    "encounters",
                    "encounter{}".format(entry["resource"]["id"]),
                )

                if path.exists() and path.is_dir():
                    shutil.rmtree(path)
                os.mkdir(path)

                file_path = os.path.join(
                    path, "encounter{}.json".format(entry["resource"]["id"])
                )
                del entry["search"]
                with open(file_path, "w") as f:
                    f.write(json.dumps(entry, indent=2))

                observations = os.path.join(path, "observations")
                os.mkdir(observations)
            enc_offset += expected_enc

    print("Done.")
