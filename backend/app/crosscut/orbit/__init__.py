"""The single Orbit client — Local (real `orbit` CLI / DuckDB) and Remote (REST) modes.

This replaces the previous eight-file sprawl. There are no mocks here: Local mode shells
out to the real `orbit` binary; Remote mode issues a real HTTP request to GitLab's Orbit
REST endpoint.
"""

from app.crosscut.orbit.client import OrbitClient, OrbitError

__all__ = ["OrbitClient", "OrbitError"]
