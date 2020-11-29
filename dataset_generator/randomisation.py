import random


class RandomGenerator:

    # 0.5 for an even distribution
    FRONT_BIAS_ORGS = 0.8
    # Practitioner bias can't be large, otherwise q4 has no interesting solutions.
    FRONT_BIAS_PRACS = 0.6

    @classmethod
    def set_all_orgs(cls, orgs):
        # Input should be a list of IDs.
        cls.ALL_ORGS = orgs

    @classmethod
    def set_all_pracs(cls, pracs):
        # Input should be a mapping from org ids to prac ids.
        cls.ALL_PRACS = pracs

    @classmethod
    def random_org(cls):
        return cls.random_select(cls.ALL_ORGS, cls.FRONT_BIAS_ORGS)

    @classmethod
    def random_prac(cls, org_id):
        return cls.random_select(cls.ALL_PRACS[org_id], cls.FRONT_BIAS_PRACS)

    @classmethod
    def random_select(cls, items, bias):
        if len(items) == 0:
            raise ValueError(
                "Random selections should always be done on a nonempty list."
            )
        lo = 0
        hi = len(items)
        while hi - lo > 1:
            if random.random() < bias:
                hi = (lo + hi) // 2
            else:
                lo = (lo + hi) // 2
        return items[lo]
