import argparse
from math import isclose
import json
import sys

def splitReceipt(items, total, subtotal, debug):
    subtotals = {}
    tableItems = []
    initial_subtotal = 0

    for item in items:
        people = item["people"]
        name = item["name"]
        cost = item["cost"]

        initial_subtotal += cost

        if people:
            subItem = {
                "name": name,
                "cost": cost / len(people),
            }

            for person in people:
                if person not in subtotals:
                    subtotals[person] = []

                subtotals[person].append(subItem)
        else:
            tableItems.append(item)

    for item in tableItems:
        name = item["name"]
        cost = item["cost"]

        subItem = {
            "name": name,
            "cost": cost / len(subtotals),
        }

        for person in subtotals.keys():
            subtotals[person].append(subItem)

    assert subtotal is None or isclose(initial_subtotal, subtotal), "Items subtotal does not match given subtotal! Expected {}, got {}".format(subtotal, initial_subtotal)

    final_totals = {}
    running_subtotal = 0
    running_total = 0

    for person, items in subtotals.items():
        person_subtotal = 0

        for item in items:
            person_subtotal += item["cost"]

        running_subtotal += person_subtotal

        person_total = person_subtotal / initial_subtotal * total
        running_total += person_total

        final_totals[person] = {
            "total": person_total,
            "items": items,
        }

    assert isclose(running_subtotal, initial_subtotal), "Split subtotal does not match initial subtotal! Expected {}, got {}".format(initial_subtotal, running_subtotal)

    assert isclose(running_total, total), "Calculated total does not equal specified total! Expected {}, got {}".format(total, running_total)

    if debug:
        print(json.dumps(final_totals, indent=4))
        print()

    for person, totals in final_totals.items():
        print("{}:\t{}".format(person, round(totals["total"], 2)))

if __name__ == '__main__':
    if sys.version_info[0] < 3:
        raise Exception('Must be using Python 3')

    parser = argparse.ArgumentParser(description='Splits the given check')

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-f', '--file', type=str)

    args = parser.parse_args()

    debug = args.debug
    file = args.file

    if file:
        with open(file) as json_file:
            data = json.load(json_file)
            subtotal = data["subtotal"] if "subtotal" in data else None
            splitReceipt(data["items"], data["total"], subtotal, debug)
    else:
        data = json.load(sys.stdin)
        subtotal = data["subtotal"] if "subtotal" in data else None
        splitReceipt(data["items"], data["total"], subtotal, debug)