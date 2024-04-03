import csv
import json
import os

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()

    out_path: str = os.getenv("OUT_PATH")

    # Load the tool output
    res: list[dict[str, str]]
    with open(out_path, "r") as f:
        res = json.load(f)

    # Load the set of tests
    tests: set[str]
    with open(os.getenv("TEST_PATH"), "r") as f:
        reader: csv.DictReader = csv.DictReader(f)
        tests = set(map(lambda row: row["ID"], reader))
    
    # Load the mappings
    map_: list[dict[str, str | list[str]]]
    with open(os.getenv("MAP_PATH"), "r") as f:
        fields: list[str] = [
            "Req ID",
            "Test IDs"
        ]
        reader: csv.DictReader = csv.DictReader(f)

        map_ = list(map(lambda row: {k: row[k] for k in row.keys() if k in fields}, reader))

        for e in map_:
            e["Test IDs"] = e["Test IDs"].replace(" ", "").split(",") if e["Test IDs"] else []

    # Values for confusion matrix
    n: int = 0
    tp: int = 0
    tn: int = 0
    fp: int = 0
    fn: int = 0

    for req in res:
        req_id: str = req["requirementID"]
        actual_tests: set[str] = set(req["tests"].replace(" ", "").split(","))

        expected_tests: set[str]
        try:
            expected_tests = set([e["Test IDs"] for e in map_ if e["Req ID"] == req_id][0])
        except:
            expected_tests = set()

        tps: set[str] = actual_tests & expected_tests
        tpsn: int = len(tps)
        fps: set[str] = actual_tests - expected_tests
        fpsn: int = len(fps)

        # Negatives
        expected_ns: set[str] = tests - expected_tests
        actual_ns: set[str] = tests - actual_tests

        tns: set[str] = actual_ns & expected_ns
        tnsn: int = len(tns)
        fns: set[str] = actual_ns - expected_ns
        fnsn: int = len(fns)

        n += tpsn + fpsn + tnsn + fnsn
        tp += tpsn
        tn += tnsn
        fp += fpsn
        fn += fnsn
    
    accuracy: float = 100 * (tp + tn) / n if n != 0 else 0
    recall: float = 100 * tp / (tp + fn) if tp + fn != 0 else 0
    precision: float = 100 * tp / (tp + fp) if tp + fp != 0 else 0

    eval_path = f"{os.path.dirname(out_path)}/eval.log"
    lines: list[str] = [
        f"{n=}",
        f"{tp=}",
        f"{tn=}",
        f"{fp=}",
        f"{fn=}",
        f"{accuracy=}%",
        f"{recall=}%",
        f"{precision=}%"
    ]
    with open(eval_path, "w+") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()