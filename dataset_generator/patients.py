import requests
import json
import os
from pathlib import Path
import shutil
import random
from .weighted_random import WeightedRandom


def generate_patients(total_patients, pracs_per_patient, api_url, api_token, directory_path):
    """
    :param directory_path: Directory containing all of the organizations
    """
    print("=== Generating patients")
    patients = []
    page_token = None
    patients_left = total_patients

    while patients_left > 0:
        request_url = api_url + 'Patient?_count={}&apikey={}'.format(
            min(1000, patients_left),
            api_token
        )
        if page_token is not None:
            request_url += '&_page_token=' + page_token

        print("Requesting ", request_url, patients_left, "remaining.")
        result = requests.get(request_url)
        print("Request made.")

        try:
            patients += (json.loads(result.text)['entry'])
            patients_left -= 1000
            all_links = json.loads(result.text)['link']
        except KeyError:
            # Request has timed out
            print("Request timed out.")
            continue

        next_link = None
        for link in all_links:
            if link['relation'] == 'next':
                next_link = link
                break

        if next_link is None and patients_left > 0:
            print('Oh no')
            break

        if patients_left > 0:
            page_token = next_link['url'].split('_page_token=')[1]

    print("Fetched {} patients".format(len(patients)))

    for patient in patients:
        # Assign an organization
        del patient["search"]
        patient["managingOrganization"] = {
            "reference": WeightedRandom.random_org()
        }
        prac_ids = list(set(WeightedRandom.random_prac() for _ in range(random.randint(*pracs_per_patient))))
        patient["generalPractitioner"] = [{"reference": prac_id} for prac_id in prac_ids]
        path = Path(directory_path, 'patient{}'.format(patient['resource']['id']))

        if path.exists() and path.is_dir():
            shutil.rmtree(path)
        os.mkdir(path)

        file_path = os.path.join(path, 'patient{}.json'.format(patient['resource']['id']))
        with open(file_path, 'w') as f:
            f.write(json.dumps(patient, indent=2))

    print("Done.")
