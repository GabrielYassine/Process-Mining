from dependency_graph import (
    read_from_file,
    dependency_graph_file
)


def read_from_file_test():
    print("=== TESTING read_from_file ===")

    event_log = read_from_file("example-log.xes")

    print("Type:", type(event_log))
    print("Number of cases:", len(event_log))

    # Show first case
    first_case = next(iter(event_log))

    print("\nFirst case:", first_case)
    print("Number of events:", len(event_log[first_case]))

    print("\nEvents:")
    for event in event_log[first_case]:
        print(event)

    # Check types
    first_event = event_log[first_case][0]

    print("\nAttribute types:")
    for key, value in first_event.items():
        print(key, "=", value, "|", type(value))


def dependency_graph_file_test():
    print("\n=== TESTING dependency_graph_file ===")

    event_log = read_from_file("example-log.xes")
    dg = dependency_graph_file(event_log)

    print("\nDependency graph:")

    for source in sorted(dg):
        for target in sorted(dg[source]):
            print(
                source,
                "->",
                target,
                ":",
                dg[source][target]
            )


def main():
    read_from_file_test()
    dependency_graph_file_test()


if __name__ == "__main__":
    main()