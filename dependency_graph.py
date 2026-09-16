import xml.etree.ElementTree as ET
from datetime import datetime


def log_as_dictionary(log):
    results = {}

    for line in log.splitlines():
        line = line.strip()

        if not line:
            continue

        task, case_id, user, timestamp = line.split(";")

        if case_id not in results:
            results[case_id] = []

        results[case_id].append({
            "task": task,
            "user": user,
            "timestamp": timestamp
        })

    return results


def dependency_graph_inline(event_log):
    df = {}

    for case_id in event_log:
        events = event_log[case_id]

        events = sorted(
            events,
            key=lambda event: event["timestamp"]
        )

        for i in range(len(events) - 1):
            source = events[i]["task"]
            target = events[i + 1]["task"]

            if source not in df:
                df[source] = {}

            if target not in df[source]:
                df[source][target] = 0

            df[source][target] += 1

    return df


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


def dependency_graph_file(event_log):
    df = {}

    for case_id in event_log:
        events = event_log[case_id]

        events = sorted(
            events,
            key=lambda event: event["time:timestamp"]
        )

        for i in range(len(events) - 1):
            source = events[i]["concept:name"]
            target = events[i + 1]["concept:name"]

            if source not in df:
                df[source] = {}

            if target not in df[source]:
                df[source][target] = 0

            df[source][target] += 1

    return df