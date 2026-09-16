import pm4py

def log_as_dictionary(log):
    event_list = log.split("\n")

    for i in range(len(event_list)):
        event_list[i] = event_list[i].strip()

    results = {}
    for event in event_list:
        task, case_id, user, timestamp = event.split(";")
        if case_id not in results:
            results[case_id] = []

        results[case_id].append(
            {
                "task": task,
                "user": user,
                "timestamp": timestamp
            }
        )

    for case in results:
        print(case, results[case])
    return results 
        

def dependency_graph_inline(event_log):
    df = {}

    for case_id in event_log:
        events = event_log[case_id]

        events = sorted(events, key=lambda event: event["timestamp"])

        for i in range(len(events) - 1):
            source = events[i]["task"]
            target = events[i + 1]["task"]

            if source not in df:
                df[source] = {}

            if target not in df[source]:
                df[source][target] = 0

            df[source][target] += 1
    for source in df:
        print(source, df[source])
    return df
    


def read_from_file(filename):
    df = pm4py.read_xes(filename)

    print(df.head())
    print(df.columns)

#def dependency_graph_file(log):

