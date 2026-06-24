"""Crosscut — graph-grounded test selection for GitLab merge requests.

On every MR, Crosscut queries GitLab Orbit's call graph to compute the minimal set
of tests that can possibly be affected by the changed code, runs only those in a
targeted child pipeline, and posts the measured saving back on the MR.

The selection core (`selection.py`) is a pure, deterministic function with no I/O
and no LLM. The Orbit client (`orbit/`) is the only component that talks to the graph.
"""

__version__ = "0.1.0"
