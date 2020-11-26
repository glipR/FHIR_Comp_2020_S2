import os
import json
import shutil
import yaml
import re


def combine_all(directory_path):
    print("=== Combining all data files")
    build_path = os.path.join(directory_path, "build")
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    os.mkdir(build_path)

    # Create a new empty file
    for key in ["sythetic_mass_bundle"]:
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
            lambda x: x != "build" and os.path.isdir(os.path.join(directory_path, x)),
            os.listdir(directory_path),
        )
    )
    for org_index, organization in enumerate(organizations):
        print("Organization {} of {}".format(org_index + 1, len(organizations)))
        org_path = os.path.join(directory_path, organization)
        with open("{}/{}.json".format(org_path, organization), "r") as f:
            org_object = json.loads(f.read())
            org_object["request"] = {"method": "POST", "url": "Organization"}

        text = json.dumps(org_object, indent=2)
        with open("{}/organization_full_data.json".format(build_path), "a") as f:
            f.write("\n    " + "\n    ".join(text.split("\n")) + ",")

        pracs = list(
            filter(
                lambda x: os.path.isdir(os.path.join(org_path, x)), os.listdir(org_path)
            )
        )

        for index, prac in enumerate(pracs):
            print("- Prac {} of {}".format(index + 1, len(pracs)))
            prac_path = os.path.join(org_path, prac)
            with open("{}/{}.json".format(prac_path, prac), "r") as f:
                prac_object = json.loads(f.read())
                prac_object["request"] = {"method": "POST", "url": "Practitioner"}

            text = json.dumps(prac_object, indent=2)
            with open("{}/practitioner_full_data.json".format(build_path), "a") as f:
                f.write("\n    " + "\n    ".join(text.split("\n")) + ",")

            patients = list(
                filter(
                    lambda x: os.path.isdir(os.path.join(prac_path, x)),
                    os.listdir(prac_path),
                )
            )
            for patient in patients:
                patient_path = os.path.join(prac_path, patient)
                with open("{}/{}.json".format(patient_path, patient), "r") as f:
                    patient_object = json.loads(f.read())
                    patient_object["request"] = {"method": "POST", "url": "Patient"}
                text = json.dumps(patient_object, indent=2)
                with open("{}/patient_full_data.json".format(build_path), "a") as f:
                    f.write("\n    " + "\n    ".join(text.split("\n")) + ",")

                encounters = []
                observations = []
                conditions = []
                medications = []

                encs = list(
                    filter(
                        lambda x: os.path.isdir(os.path.join(patient_path, x)),
                        os.listdir(patient_path),
                    )
                )
                for encounter in encs:
                    encounter_path = os.path.join(patient_path, encounter)
                    with open("{}/{}.json".format(encounter_path, encounter), "r") as f:
                        encounter_object = json.loads(f.read())
                        encounter_object["request"] = {
                            "method": "POST",
                            "url": "Encounter",
                        }
                    text = json.dumps(encounter_object, indent=2)
                    with open(
                        "{}/encounter_full_data.json".format(build_path), "a"
                    ) as f:
                        f.write("\n    " + "\n    ".join(text.split("\n")) + ",")
                    encounters.append(encounter_object)

                    obss = list(
                        filter(
                            lambda x: (
                                os.path.isdir(os.path.join(encounter_path, x))
                                and x.startswith("observation")
                            ),
                            os.listdir(encounter_path),
                        )
                    )
                    for observation in obss:
                        observation_path = os.path.join(encounter_path, observation)
                        with open(
                            "{}/{}.json".format(observation_path, observation), "r"
                        ) as f:
                            observation_object = json.loads(f.read())
                            observation_object["request"] = {
                                "method": "POST",
                                "url": "Observation",
                            }
                        text = json.dumps(observation_object, indent=2)
                        with open(
                            "{}/observation_full_data.json".format(build_path), "a"
                        ) as f:
                            f.write("\n    " + "\n    ".join(text.split("\n")) + ",")
                        observations.append(observation_object)

                    conds = list(
                        filter(
                            lambda x: (
                                os.path.isdir(os.path.join(encounter_path, x))
                                and x.startswith("condition")
                            ),
                            os.listdir(encounter_path),
                        )
                    )
                    for condition in conds:
                        condition_path = os.path.join(encounter_path, condition)
                        with open(
                            "{}/{}.json".format(condition_path, condition), "r"
                        ) as f:
                            condition_object = json.loads(f.read())
                            condition_object["request"] = {
                                "method": "POST",
                                "url": "Condition",
                            }
                        text = json.dumps(condition_object, indent=2)
                        with open(
                            "{}/condition_full_data.json".format(build_path), "a"
                        ) as f:
                            f.write("\n    " + "\n    ".join(text.split("\n")) + ",")
                        conditions.append(condition_object)

                    meds = list(
                        filter(
                            lambda x: (
                                os.path.isdir(os.path.join(encounter_path, x))
                                and x.startswith("medication")
                            ),
                            os.listdir(encounter_path),
                        )
                    )
                    for medication in meds:
                        medication_path = os.path.join(encounter_path, medication)
                        with open(
                            "{}/{}.json".format(medication_path, medication), "r"
                        ) as f:
                            medication_object = json.loads(f.read())
                            medication_object["request"] = {
                                "method": "POST",
                                "url": "MedicationRequest",
                            }
                        text = json.dumps(medication_object, indent=2)
                        with open(
                            "{}/medicationrequest_full_data.json".format(build_path),
                            "a",
                        ) as f:
                            f.write("\n    " + "\n    ".join(text.split("\n")) + ",")
                        medications.append(medication_object)

    bundle_file = open("{}/{}.json".format(build_path, "sythetic_mass_bundle"), "a")
    for key in [
        "patient",
        "organization",
        "practitioner",
        "observation",
        "condition",
        "medicationrequest",
        "encounter",
    ]:
        if os.path.isfile("{}/{}_full_data.json".format(build_path, key)) == False:
            continue
        json_file = open("{}/{}_full_data.json".format(build_path, key), "r")
        bundle_file.write(json_file.read())

    for key in ["sythetic_mass_bundle"]:
        with open("{}/{}.json".format(build_path, key), "a") as f:
            bundle = """
  ]
}\
"""
            f.write(bundle)

    for key in ["sythetic_mass_bundle"]:
        json_file = open("{}/{}.json".format(build_path, key), "r+")
        fix_urn_data = re.sub(
            "[a-zA-Z]*https:\/\/syntheticmass.mitre.org\/v1\/fhir\/[a-zA-Z]*\/",
            "urn:uuid:",
            json_file.read(),
            flags=re.MULTILINE,
        )
        data = yaml.load(fix_urn_data, yaml.SafeLoader)
        json_file.seek(0)
        json_file.truncate()
        json_file.write(json.dumps(data, indent=2))
        json_file.close()

    print("Done.")
