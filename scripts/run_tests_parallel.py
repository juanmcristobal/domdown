"""Run pytest in balanced, isolated worker processes without third-party plugins."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
NODE_ID_LINE = re.compile(r"^tests/.*\.py::")


def _parse_args() -> tuple[int, list[str]]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-j",
        "--workers",
        type=int,
        default=min(os.cpu_count() or 1, 8),
        help="maximum concurrent pytest processes (default: up to 8)",
    )
    args, pytest_args = parser.parse_known_args()
    if pytest_args and pytest_args[0] == "--":
        pytest_args = pytest_args[1:]
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if any(arg == "--basetemp" or arg.startswith("--basetemp=") for arg in pytest_args):
        parser.error("--basetemp is managed separately for each worker")
    return args.workers, pytest_args


def _collect_node_ids(pytest_args: list[str], env: dict[str, str]) -> list[str]:
    command = [sys.executable, "-m", "pytest", *pytest_args, "--collect-only", "-q"]
    result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
    if result.returncode:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    node_ids = [line.strip() for line in result.stdout.splitlines() if NODE_ID_LINE.match(line.strip())]
    if not node_ids:
        sys.stdout.write(result.stdout)
        raise SystemExit("pytest collection returned no test items")
    return node_ids


def _estimated_cost(node_id: str) -> float:
    """Estimate item durations from recent pytest ``--durations`` measurements."""

    measured = (
        ("oracle_cpu_october_2026", "equivalent", 38.5),
        ("oracle_cpu_october_2026", "replay", 21.4),
        ("bleepingcomputer_november_2026_patch_tuesday", "equivalent", 13.8),
        ("bleepingcomputer_november_2026_patch_tuesday", "replay", 8.9),
        ("oracle_cpun_table", "", 7.5),
        ("oracle_cpu_october_2026", "test_real_example_cases_match", 7.4),
        ("wikipedia_elliptic_curve_cryptography", "equivalent", 3.9),
        ("wikipedia_elliptic_curve_cryptography", "replay", 3.5),
        ("endorlabs_openclaw_ai_sast_vulnerabilities", "equivalent", 3.0),
        ("bushidotoken_blackbasta_leaks_lessons_from_ascension", "equivalent", 2.4),
        ("aikido_axios_npm_compromised_maintainer_hijacked_rat", "equivalent", 2.0),
        ("fortinet_threat_report_automated_cyberattacks", "equivalent", 1.9),
        ("bushidotoken_blackbasta_leaks_lessons_from_ascension", "replay", 1.8),
    )
    for case_id, test_marker, duration in measured:
        if case_id in node_id and test_marker in node_id:
            return duration
    return 1.2


def _make_shards(node_ids: list[str], workers: int) -> list[list[str]]:
    shard_count = min(workers, len(node_ids))
    shards: list[list[str]] = [[] for _ in range(shard_count)]
    loads = [0] * shard_count
    for node_id in sorted(node_ids, key=_estimated_cost, reverse=True):
        shard = min(range(shard_count), key=loads.__getitem__)
        shards[shard].append(node_id)
        loads[shard] += _estimated_cost(node_id)
    return shards


def _run_shard(index: int, nodes: list[str], pytest_args: list[str], base_temp: Path, env: dict[str, str]):
    command = [
        sys.executable,
        "-m",
        "pytest",
        *pytest_args,
        "-q",
        f"--basetemp={base_temp / f'worker-{index + 1}'}",
        *nodes,
    ]
    return index, nodes, subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)


def main() -> int:
    workers, pytest_args = _parse_args()
    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    node_ids = _collect_node_ids(pytest_args, env)
    shards = _make_shards(node_ids, workers)
    print(f"Collected {len(node_ids)} tests; running {len(shards)} shards")
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="domdown-pytest-") as temp_dir:
        base_temp = Path(temp_dir)
        results = []
        with ThreadPoolExecutor(max_workers=len(shards)) as executor:
            futures = [
                executor.submit(_run_shard, index, shard, pytest_args, base_temp, env)
                for index, shard in enumerate(shards)
            ]
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                index, nodes, completed = result
                print(f"\n--- shard {index + 1}/{len(shards)} ({len(nodes)} tests) exit={completed.returncode} ---")
                sys.stdout.write(completed.stdout)
                sys.stderr.write(completed.stderr)
    elapsed = time.perf_counter() - started
    failed = [result for result in results if result[2].returncode]
    print(f"\n{len(node_ids)} tests across {len(shards)} shards in {elapsed:.2f}s")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
