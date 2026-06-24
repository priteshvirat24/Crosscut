"""Crosscut CLI — the runtime entrypoint the GitLab flow invokes.

End to end:  diff  ->  Orbit query  ->  deterministic selection  ->  targeted child
pipeline (YAML artifact)  +  MR comment.  No mocks anywhere in this path.

    python -m app.crosscut.cli \
        --repo . --diff changes.diff \
        --out-pipeline crosscut-targeted.yml --out-comment crosscut-comment.md \
        [--index] [--measure] [--post]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict

from app.crosscut import diff as diffmod
from app.crosscut.comment import render_comment
from app.crosscut.config import CrosscutConfig
from app.crosscut.models import Mode, TimingResult
from app.crosscut.orbit import OrbitClient, OrbitError
from app.crosscut.pipeline import generate_pipeline, to_yaml
from app.crosscut.selection import select_tests


def _read_diff(args: argparse.Namespace) -> str:
    if args.diff == "-":
        return sys.stdin.read()
    if args.diff:
        with open(args.diff, encoding="utf-8") as fh:
            return fh.read()
    if args.git_range:
        proc = subprocess.run(
            ["git", "-C", args.repo, "diff", args.git_range],
            capture_output=True,
            text=True,
        )
        return proc.stdout
    raise SystemExit("Provide --diff <file|-> or --git-range <A..B>")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="crosscut", description=__doc__)
    p.add_argument("--repo", default=".", help="Path to the repository (default: .)")
    p.add_argument("--diff", help="Path to a unified diff file, or '-' for stdin")
    p.add_argument("--git-range", help="Compute the diff from a git range, e.g. main...HEAD")
    p.add_argument("--index", action="store_true", help="(Re)index the repo with Orbit first")
    p.add_argument("--measure", action="store_true", help="Measure full-vs-selected runtime")
    p.add_argument("--post", action="store_true", help="Post the comment to the MR via the API")
    p.add_argument("--out-pipeline", default="crosscut-targeted.yml")
    p.add_argument("--out-comment", default="crosscut-comment.md")
    p.add_argument("--out-json", default="crosscut-results.json")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = CrosscutConfig.from_env()
    client = OrbitClient.from_config(config)

    if args.index:
        if config.orbit_mode is not Mode.LOCAL:
            print("crosscut: --index ignored (not Local mode)", file=sys.stderr)
        else:
            stats = client.index(args.repo)
            g = stats.get("graph", {})
            print(
                f"crosscut: indexed {g.get('files', '?')} files, "
                f"{g.get('definitions', '?')} definitions",
                file=sys.stderr,
            )

    diff_text = _read_diff(args)
    changed = diffmod.parse_diff(diff_text)
    print(
        f"crosscut: {len(changed)} changed symbol(s) in "
        f"{len(diffmod.changed_files(diff_text))} file(s)",
        file=sys.stderr,
    )

    try:
        graph = client.build_graph()
        inventory = client.build_inventory(graph)
    except OrbitError as exc:
        print(f"crosscut: Orbit query failed: {exc}", file=sys.stderr)
        return 2

    result = select_tests(changed, graph, inventory, mode=config.orbit_mode)
    print(
        f"crosscut: selected {result.metrics.selected_tests}/{result.metrics.total_tests} "
        f"tests ({result.metrics.percentage_reduction:.0f}% fewer), "
        f"full_suite={result.run_full_suite}",
        file=sys.stderr,
    )

    timing: TimingResult | None = None
    if args.measure:
        from app.crosscut.runner import measure

        timing = measure(result, test_command=config.test_command, cwd=args.repo)
        print(
            f"crosscut: measured {timing.full_suite_seconds}s -> "
            f"{timing.selected_seconds}s ({timing.seconds_saved}s saved)",
            file=sys.stderr,
        )

    pipeline = generate_pipeline(
        result,
        test_command=config.test_command,
        image=config.ci_image,
        before_script=list(config.ci_before_script) or None,
    )
    with open(args.out_pipeline, "w", encoding="utf-8") as fh:
        fh.write(to_yaml(pipeline))

    comment = render_comment(result, timing=timing, changed_symbols=[c.name for c in changed])
    with open(args.out_comment, "w", encoding="utf-8") as fh:
        fh.write(comment)
    print(f"crosscut: wrote {args.out_pipeline} and {args.out_comment}", file=sys.stderr)

    if args.out_json:
        out_data = {
            "metrics": result.metrics.as_dict(),
            "run_full_suite": result.run_full_suite,
            "selected_tests": [asdict(t) for t in result.selected],
            "changed_symbols": [c.name for c in changed],
        }
        if timing:
            out_data["timing"] = {
                "full_suite_seconds": timing.full_suite_seconds,
                "selected_seconds": timing.selected_seconds,
                "seconds_saved": timing.seconds_saved,
                "measured": timing.measured,
            }

        with open(args.out_json, "w", encoding="utf-8") as fh:
            json.dump(out_data, fh, indent=2)
        print(f"crosscut: wrote {args.out_json}", file=sys.stderr)

    if args.post:
        from app.crosscut.gitlab import GitLabError, post_mr_note

        try:
            post_mr_note(config, comment)
            print("crosscut: posted MR comment", file=sys.stderr)
        except GitLabError as exc:
            print(f"crosscut: could not post comment: {exc}", file=sys.stderr)
            return 3

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
