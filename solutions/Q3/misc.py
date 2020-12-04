from dateutil import parser

def total_serum_required(d, prac_id):
    serum = 0

    for pat_id in d["practitioners"][prac_id].patients:
        pat = d["patients"][pat_id]
        pat.platelets = None
    
        for obs_id in pat.observations:
            if d["observations"][obs_id].code != "32623-1":
                continue
            if pat.platelets is None or pat.platelets[1] < parser.parse(d["observations"][obs_id].effective):
                pat.platelets = (
                    (d["observations"][obs_id].value["value"], d["observations"][obs_id].value["unit"]),
                    parser.parse(d["observations"][obs_id].effective),
                )
        if pat.platelets is not None:
            serum += 10 + 20*pat.platelets[0][0]
    return serum
