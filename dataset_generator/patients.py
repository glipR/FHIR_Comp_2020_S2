from random import Random
import requests
import json
import os
from pathlib import Path
import shutil
import random
from .randomisation import RandomGenerator


def generate_patients(
    total_patients, pracs_per_patient, api_url, api_token, directory_path
):
    """
    :param directory_path: Directory containing all of the organizations
    """
    print("=== Generating patients")
    patients = []
    patients_left = total_patients
    page_token = None

    while patients_left > 0:
        request_url = api_url + "Patient?_count={}&apikey={}".format(
            min(1000, patients_left), api_token
        )
        if page_token is not None:
            request_url += "&_page_token=" + page_token

        print("Requesting ", request_url, patients_left, "remaining.")
        result = requests.get(request_url)
        print("Request made.")

        try:
            patients += json.loads(result.text)["entry"]
            patients_left -= 1000
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

        if next_link is None and patients_left > 0:
            print("Oh no")
            break

        if patients_left > 0:
            page_token = next_link["url"].split("_page_token=")[1]

    print("Fetched {} patients".format(len(patients)))

    for patient in patients:
        org = RandomGenerator.random_org()
        num_pracs = random.randint(*pracs_per_patient)
        pracs = set([RandomGenerator.random_prac(org) for _ in range(num_pracs)])

        patient["resource"]["managingOrganization"] = {"reference": f"urn:uuid:{org}"}
        patient["resource"]["generalPractitioner"] = [
            {"reference": f"urn:uuid:{prac_id}"} for prac_id in pracs
        ]
        del patient["search"]

        patient_path = os.path.join(
            directory_path, "organizations/organization{}".format(org), "patients"
        )
        dirpath = os.path.join(
            patient_path, "patient{}".format(patient["resource"]["id"])
        )
        filename = os.path.join(
            dirpath, "patient{}.json".format(patient["resource"]["id"])
        )
        os.mkdir(dirpath)
        with open(filename, "w") as f:
            f.write(json.dumps(patient, indent=2))
        encounter_path = os.path.join(dirpath, "encounters")
        os.mkdir(encounter_path)

    print("Done.")
