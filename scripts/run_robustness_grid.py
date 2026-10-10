"""Run the R1-R5 robustness grid in priority order on one machine.

Order: R1 (N=200 primary/control, seeds 0-7), R2 (gain-matched), R3 (frozen
drive), R5 (seeds 8-15), R4 (N=100, then N=400).  Session 2 blocks: R2x/R3x
(R2/R3 seeds 8-15), B3 (random-subset equal-budget control), B4 (R3 with
unmatched total gain); select them with ``--only``.  Finished tasks are skipped,
so the command can be interrupted and restarted.  Pass ``--only`` to run a
subset, e.g. ``--only R1,R2,R3``.
"""

import argparse
import time

from nma_motor_rnn.robustness import collect, make_tasks, run_tasks

GRID = {
    "R1": [(("primary", "control"), 200, range(0, 8))],
    "R2": [(("primary_gain", "control_gain"), 200, range(0, 8))],
    "R3": [(("frozen",), 200, range(0, 8))],
    # Session 2: extend R2/R3 to 16 seeds.
    "R2x": [(("primary_gain", "control_gain"), 200, range(8, 16))],
    "R3x": [(("frozen",), 200, range(8, 16))],
    "B3": [(("control_random",), 200, range(0, 8))],  # vs primary seeds 0-7 (R1)
    "B4": [(("frozen_unmatched",), 200, range(0, 8))],
    "R5": [(("primary", "control"), 200, range(8, 16))],
    "R4": [
        (("primary", "control"), 100, range(0, 8)),
        (("primary", "control"), 400, range(0, 8)),
    ],
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="R1,R2,R3,R5,R4")
    parser.add_argument("--out", default="results/robustness")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    tasks = []
    for key in args.only.split(","):
        for arms, n_units, seeds in GRID[key]:
            block = make_tasks(args.out, arms, n_units, list(seeds))
            # Longest (densest) networks first inside a block for load balance.
            block.sort(key=lambda task: -task[4].p_value)
            tasks.extend(block)
    start = time.perf_counter()
    run_tasks(tasks, args.workers)
    print(f"{len(tasks)} tasks finished in {time.perf_counter() - start:.1f}s wall")
    collect(args.out)


if __name__ == "__main__":
    main()
