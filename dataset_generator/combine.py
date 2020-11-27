import os
import json
import shutil
import re


def combine_all(directory_path):
    print("=== Combining all data files")
    build_path = os.path.join(directory_path, "build")
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.mkdir(build_path)

    # Create a new empty file
    for key in ["organizations", "practitioners", "patients", "encounters", "observations"]:
        with open("{}/{}.json".format(build_path, key), "w") as f:
            bundle = """\
{
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [\
    """
            f.write(bundle)

    organizations = list(
        filter(
            lambda x: os.path.isdir(os.path.join(directory_path, "organizations", x)),
            os.listdir(os.path.join(directory_path, "organizations")),
        )
    )
    for org_index, organization in enumerate(organizations):
        org_path = os.path.join(directory_path, "organizations", organization)
        with open("{}/{}.json".format(org_path, organization), "r") as f:
            org_object = json.loads(f.read())
            org_object["request"] = {"method": "POST", "url": "Organization"}

        text = json.dumps(org_object, indent=2)
        with open("{}/organizations.json".format(build_path), "a") as f:
            f.write("\n    " + "\n    ".join(text.split("\n")) + ",")

        patients = list(
            filter(
                lambda x: os.path.isdir(os.path.join(org_path, "patients", x)),
                os.listdir(os.path.join(org_path, "patients")),
            )
        )
        for patient in patients:
            patient_path = os.path.join(org_path, "patients", patient)
            with open("{}/{}.json".format(patient_path, patient), "r") as f:
                patient_object = json.loads(f.read())
                patient_object["request"] = {"method": "POST", "url": "Patient"}
            text = json.dumps(patient_object, indent=2)
            with open("{}/patients.json".format(build_path), "a") as f:
                f.write("\n    " + "\n    ".join(text.split("\n")) + ",")

            encs = list(
                filter(
                    lambda x: os.path.isdir(os.path.join(patient_path, "encounters", x)),
                    os.listdir(os.path.join(patient_path, "encounters")),
                )
            )
            for encounter in encs:
                encounter_path = os.path.join(patient_path, "encounters", encounter)
                with open("{}/{}.json".format(encounter_path, encounter), "r") as f:
                    encounter_object = json.loads(f.read())
                    encounter_object["request"] = {
                        "method": "POST",
                        "url": "Encounter",
                    }
                text = json.dumps(encounter_object, indent=2)
                with open(
                    "{}/encounters.json".format(build_path), "a"
                ) as f:
                    f.write("\n    " + "\n    ".join(text.split("\n")) + ",")

                obss = list(os.listdir(os.path.join(encounter_path, "observations")))
                for observation in obss:
                    observation_path = os.path.join(encounter_path, "observations", observation)
                    with open(observation_path, "r") as f:
                        observation_object = json.loads(f.read())
                        observation_object["request"] = {
                            "method": "POST",
                            "url": "Observation",
                        }
                    text = json.dumps(observation_object, indent=2)
                    with open(
                        "{}/observations.json".format(build_path), "a"
                    ) as f:
                        f.write("\n    " + "\n    ".join(text.split("\n")) + ",")

    pracs = os.listdir(os.path.join(directory_path, "all_practitioners"))

    for prac in pracs:
        prac_path = os.path.join(directory_path, "all_practitioners", prac)
        with open(prac_path, "r") as f:
            prac_object = json.loads(f.read())
            prac_object["request"] = {"method": "POST", "url": "Practitioner"}

        text = json.dumps(prac_object, indent=2)
        with open("{}/practitioners.json".format(build_path), "a") as f:
            f.write("\n    " + "\n    ".join(text.split("\n")) + ",")

    for key in ["organizations", "practitioners", "patients", "encounters", "observations"]:
        with open("{}/{}.json".format(build_path, key), "a") as f:
            bundle = """
  ]
}\
"""
            f.write(bundle)

    for key in ["organizations", "practitioners", "patients", "encounters", "observations"]:
        json_file = open("{}/{}.json".format(build_path, key), "r+")
        fix_urn_data = re.sub(
            "[a-zA-Z]*https:\/\/syntheticmass.mitre.org\/v1\/fhir\/[a-zA-Z]*\/",
            "urn:uuid:",
            json_file.read(),
            flags=re.MULTILINE,
        )
        # Find the last comma and remove it
        for index in range(1, len(fix_urn_data) + 1):
            if fix_urn_data[-index] == ",":
                fix_urn_data = fix_urn_data[:-index] + fix_urn_data[-(index - 1):]
                break
        data = json.loads(fix_urn_data)
        json_file.seek(0)
        json_file.truncate()
        json_file.write(json.dumps(data, indent=2))
        json_file.close()

    print("Done.")
