# TOTAL AMOUNTS
NUMBER_PATIENTS = 500
NUMBER_OF_PRACTITIONERS = 20
NUMBER_OF_ORGANIZATIONS = 10

# MAXIMUM REQUIRED QUERIES
MAX_NUMBER_ENCOUNTERS = 1200

# MAPPING AMOUNTS
ENCOUNTERS_PER_PATIENT = [0.9, 3.2]
PRACS_PER_PATIENT = [1, 5]
PRACS_PER_ENCOUNTER = [1, 3.5]

########### OBSERVATIONS ####################
OBSERVATION_ONE = ['2339-0', 'Glucose', [1, 3]]
OBSERVATION_TWO = ['39156-5', 'Body_Mass_Index', [0.8, 3]]
OBSERVATION_THREE = ['55284-4', 'Blood_Pressure', [0.8, 1.8]]
##OBSERVATION_THREE = ['8867-4', 'Heart_Rate', [0.5, 1]]
OBSERVATION_FOUR = ['2085-9', 'HDL Cholesterol', [0.5, 1.5]]
OBSERVATION_FIVE = ['72166-2', 'Tobacco Smokimg Status', [0.5, 1.5]]
OBSERVATION_LIST = [OBSERVATION_ONE]
#############################################

API_TOKEN = 'b6ai0PI8aEEGrUGnMA18zAZsfqaBbFdD'
API_URL = 'https://syntheticmass.mitre.org/v1/fhir/'

import os
import shutil
from .randomisation import RandomGenerator
dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'dataset')

if os.path.exists(dataset_path):
    shutil.rmtree(dataset_path)
os.mkdir(dataset_path)

os.mkdir(os.path.join(dataset_path, "all_practitioners"))

# Generate organizations, and practitioners for each organization.

from .organizations import generate_organizations
RandomGenerator.set_all_orgs(generate_organizations(NUMBER_OF_ORGANIZATIONS, API_URL, API_TOKEN, dataset_path))

from .practitioners import generate_practitioners
RandomGenerator.set_all_pracs(generate_practitioners(NUMBER_OF_PRACTITIONERS, API_URL, API_TOKEN, dataset_path))

# Generate patients, give them an organization, and pick some practitioners from that organization.

from .patients import generate_patients
generate_patients(NUMBER_PATIENTS, PRACS_PER_PATIENT, API_URL, API_TOKEN, dataset_path)

# Generate encounters for a particular patient

from .encounters import generate_encounters
generate_encounters(ENCOUNTERS_PER_PATIENT, MAX_NUMBER_ENCOUNTERS, PRACS_PER_ENCOUNTER, API_URL, API_TOKEN, dataset_path)

# Generate observations for each encounter

from .observations import generate_observations
generate_observations(OBSERVATION_LIST, MAX_NUMBER_ENCOUNTERS, API_URL, API_TOKEN, dataset_path)

from .validator import validate_unique_patients
uniqueness = validate_unique_patients(dataset_path)
if not uniqueness[0]:
    print("Duplicate Patients!")
else:
    print("{} unique patients checked.".format(uniqueness[1]))
    # OUTPUT WAS: 193100 unique patients checked.

# from .combine import combine_all
# combine_all(dataset_path)

#combined_dataset_path = os.path.join(dataset_path, 'build')
#from replace_practitioner import merge_big_practitioners
#merge_big_practitioners(combined_dataset_path)
