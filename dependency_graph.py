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
        

#def dependency_graph_inline(log):

#def read_from_file(filename):

#def dependency_graph_file(log):

