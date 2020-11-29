class Resource:
    def __init__(self, data, all_objects):
        self.id = data["resource"]["id"]
        if "active" in data["resource"] and not data["resource"]["active"]:
            print("Inactive {} found".format(data["resource"]["resourceType"]))


class Organization(Resource):
    def __init__(self, data, all_objects):
        super().__init__(data, all_objects)
        if len(data["resource"]["address"]) > 1:
            print("Organization found with more than one address")

        address = data["resource"]["address"][0]

        self.country = str(address["country"]).lower()
        self.state = str(address["state"]).lower()
        self.city = str(address["city"]).lower()
        self.post_code = str(address["postalCode"])

        self.name = data["resource"]["name"]

        self.practitioners = []
        self.patients = []


class Practitioner(Resource):
    def __init__(self, data, all_objects):
        super().__init__(data, all_objects)

        self.patients = []
        self.organizations = []


class Patient(Resource):
    def __init__(self, data, all_objects):
        super().__init__(data, all_objects)

        self.gender = data["resource"]["gender"]

        self.identifier = data['resource']['identifier']

        self.organization = data["resource"]["managingOrganization"]["reference"].split(":")[-1]
        self.practitioners = [
            obj["reference"].split(":")[-1]
            for obj in data["resource"]["generalPractitioner"]
        ]
        self.encounters = []
        self.observations = []
        all_objects["organizations"][self.organization].patients.append(self.id)
        for prac in self.practitioners:
            all_objects["practitioners"][prac].patients.append(self.id)
        for prac in self.practitioners:
            all_objects["organizations"][self.organization].practitioners.append(prac)
            all_objects["practitioners"][prac].organizations.append(self.organization)


class Encounter(Resource):
    def __init__(self, data, all_objects):
        super().__init__(data, all_objects)

        self.patient = data["resource"]["subject"]["reference"].split(":")[-1]
        self.practitioners = list(map(lambda x: x["individual"]["reference"].split(":")[-1], data["resource"]["participant"]))
        self.period_start = data["resource"]["period"]["start"]
        all_objects["patients"][self.patient].encounters.append(self.id)


class Observation(Resource):
    def __init__(self, data, all_objects):
        super().__init__(data, all_objects)

        self.code = data["resource"]["code"]["coding"][0]["code"]
        self.value = data["resource"].get("valueQuantity", None)

        try:
            self.valueCode = data['resource']['valueCodeableConcept']['coding'][0]['code']
        except Exception:
            self.valueCode = None

        self.effective = data["resource"]["effectiveDateTime"]
        self.component = data["resource"].get("component", [])

        self.encounter = data["resource"]["context"]["reference"].split("/")[1]
        self.patient = data["resource"]["subject"]["reference"].split(":")[-1]
        all_objects["patients"][self.patient].observations.append(self.id)
