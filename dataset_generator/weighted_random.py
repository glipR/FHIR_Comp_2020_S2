import random

class WeightedRandom:

    # 0.5 for an even distribution
    FRONT_BIAS_ORGS = 0.8
    FRONT_BIAS_PRACS = 0.8

    @classmethod
    def set_all_orgs(cls, orgs):
        # Input should be a list of IDs.
        cls.ALL_ORGS = orgs
    
    @classmethod
    def set_all_pracs(cls, pracs):
        # Input should be a list of IDs.
        cls.ALL_PRACS = pracs

    @classmethod
    def random_org(cls):
        return cls.random_select(cls.ALL_ORGS, cls.FRONT_BIAS_ORGS)

    @classmethod
    def random_prac(cls):
        return cls.random_select(cls.ALL_PRACS, cls.FRONT_BIAS_PRACS)

    @classmethod
    def random_select(cls, items, bias):
        lo = 0
        hi = len(items)
        while hi - lo > 1:
            if random.random() < bias:
                hi = (lo + hi) // 2
            else:
                lo = (lo + hi) // 2
        return items[lo]

