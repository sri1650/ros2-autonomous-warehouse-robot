# Contributing

1. Create a focused branch.
2. Keep ROS interfaces backward compatible or document the migration.
3. Add unit tests for deterministic logic and a launch/integration test for node wiring.
4. Run `colcon test` and `ruff check` before opening a pull request.
5. Update verification evidence when changing robot behaviour or safety thresholds.

Commit messages should explain the engineering intent, for example: `feat(safety): stop on stale velocity commands`.
