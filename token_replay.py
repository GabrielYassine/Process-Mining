import xml.etree.ElementTree as ET
from datetime import datetime
from itertools import combinations


class PetriNet():

    def __init__(self):
        self.places = []
        self.transitions = []
        self.relations = []

    def add_place(self, id):
        self.places.append(
            {
                "id": id,
                "tokens": 0
            }
        )

    def add_transition(self, name, id):
        self.transitions.append(
            {
                "name": name,
                "id": id
            }
        )

    def get_from_id(self, id):
        if id > 0:
            for place in self.places:
                if place["id"] == id:
                    return place
        else:
            for transition in self.transitions:
                if transition["id"] == id:
                    return transition

    def add_edge(self, source_id, target_id):
        self.relations.append(
            {
                "source": self.get_from_id(source_id),
                "target": self.get_from_id(target_id)
            }
        )
        return self

    def get_tokens(self, place_id):
        for place in self.places:
            if place["id"] == place_id:
                return place["tokens"]

    def is_enabled(self, transition_id):
        for edge in self.relations:
            if edge["target"]["id"] == transition_id:
                if edge["source"]["tokens"] < 1:
                    return False
        return True

    def add_marking(self, place_id):
        for place in self.places:
            if place["id"] == place_id:
                place["tokens"] += 1

    def fire_transition(self, transition_id):
        for edge in self.relations:
            if edge["source"]["id"] == transition_id:
                edge["target"]["tokens"] += 1
            elif edge["target"]["id"] == transition_id:
                edge["source"]["tokens"] -= 1

    def transition_name_to_id(self, name):
        for transition in self.transitions:
            if transition["name"] == name:
                return transition["id"]
        return None


def read_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    results = {}

    for trace in root:

        if trace.tag.split("}")[-1] != "trace":
            continue

        case_id = None
        events = []

        for child in trace:
            child_type = child.tag.split("}")[-1]

            if child_type != "event":
                if child.attrib.get("key") == "concept:name":
                    case_id = child.attrib.get("value")

            else:
                event = {}

                for attribute in child:
                    key = attribute.attrib["key"]
                    value = attribute.attrib["value"]

                    attribute_type = attribute.tag.split("}")[-1]

                    if attribute_type == "date":
                        value = datetime.fromisoformat(value).replace(
                            tzinfo=None
                        )

                    elif attribute_type == "int":
                        value = int(value)

                    elif attribute_type == "float":
                        value = float(value)

                    elif attribute_type == "boolean":
                        value = value.lower() == "true"

                    event[key] = value

                events.append(event)

        if case_id is not None:
            results[case_id] = events

    return results


def alpha(log):
    traces = []

    for case_id in log:
        events = log[case_id]

        events = sorted(
            events,
            key=lambda event: event["time:timestamp"]
        )

        trace = []

        for event in events:
            trace.append(event["concept:name"])

        traces.append(trace)

    activities = set()
    start_activities = set()
    end_activities = set()

    for trace in traces:
        if len(trace) == 0:
            continue

        activities.update(trace)
        start_activities.add(trace[0])
        end_activities.add(trace[-1])

    directly_follows = set()

    for trace in traces:
        for i in range(len(trace) - 1):
            a = trace[i]
            b = trace[i + 1]

            directly_follows.add((a, b))

    causality = set()
    parallel = set()
    choice = set()

    for a in activities:
        for b in activities:
            ab = (a, b) in directly_follows
            ba = (b, a) in directly_follows

            if ab and not ba:
                causality.add((a, b))

            elif ab and ba:
                parallel.add((a, b))

            elif not ab and not ba:
                choice.add((a, b))

    activity_list = list(activities)
    subsets = []

    for size in range(1, len(activity_list) + 1):
        for combination in combinations(activity_list, size):
            subsets.append(set(combination))

    Xw = []

    for A in subsets:
        for B in subsets:
            valid = True

            for a in A:
                for b in B:
                    if (a, b) not in causality:
                        valid = False

            if not valid:
                continue

            for a1 in A:
                for a2 in A:
                    if a1 != a2 and (a1, a2) not in choice:
                        valid = False

            if not valid:
                continue

            for b1 in B:
                for b2 in B:
                    if b1 != b2 and (b1, b2) not in choice:
                        valid = False

            if valid:
                Xw.append((A, B))

    Yw = []

    for A, B in Xw:
        maximal = True

        for A2, B2 in Xw:
            if A == A2 and B == B2:
                continue

            if A.issubset(A2) and B.issubset(B2):
                maximal = False
                break

        if maximal:
            Yw.append((A, B))

    pn = PetriNet()

    transition_ids = {}
    transition_id = -1

    for activity in activities:
        pn.add_transition(activity, transition_id)
        transition_ids[activity] = transition_id
        transition_id -= 1

    place_id = 1

    initial_place = place_id
    pn.add_place(initial_place)

    place_id += 1

    for activity in start_activities:
        pn.add_edge(
            initial_place,
            transition_ids[activity]
        )

    for A, B in Yw:
        current_place = place_id

        pn.add_place(current_place)

        for a in A:
            pn.add_edge(
                transition_ids[a],
                current_place
            )

        for b in B:
            pn.add_edge(
                current_place,
                transition_ids[b]
            )

        place_id += 1

    final_place = place_id
    pn.add_place(final_place)

    for activity in end_activities:
        pn.add_edge(
            transition_ids[activity],
            final_place
        )

    pn.add_marking(initial_place)

    return pn



def replay_trace(events, model):
    start_id = model.places[0]["id"]
    end_id = model.places[-1]["id"]

    marking = {}

    for place in model.places:
        marking[place["id"]] = 0

    marking[start_id] = 1

    m = 0  
    c = 0  
    r = 0  
    p = 1
    events = sorted(
        events,
        key=lambda event: event["time:timestamp"]
    )

    for event in events:
        name = event["concept:name"]
        transition_id = model.transition_name_to_id(name)
        for edge in model.relations:
            if edge["target"]["id"] == transition_id:
                place_id = edge["source"]["id"]

                if marking[place_id] == 0:
                    m += 1
                    marking[place_id] += 1

                marking[place_id] -= 1
                c += 1
        for edge in model.relations:
            if edge["source"]["id"] == transition_id:

                place_id = edge["target"]["id"]

                marking[place_id] += 1
                p += 1

    if marking[end_id] == 0:
        m += 1
        marking[end_id] += 1

    marking[end_id] -= 1
    c += 1

    r = sum(marking.values())

    return m, c, r, p

def fitness_token_replay(log, model):
    M = 0
    C = 0
    R = 0
    P = 0

    for case_id in log:
        events = log[case_id]

        m, c, r, p = replay_trace(events, model)

        M += m
        C += c
        R += r
        P += p

    if C == 0 or P == 0:
        raise ValueError("Cannot calculate fitness")

    fitness = 0.5 * (1 - M / C) + 0.5 * (1 - R / P)

    return fitness
