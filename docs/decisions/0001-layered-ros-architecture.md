# ADR 0001: Separate mission, navigation, safety, and hardware layers

- Status: Accepted
- Date: 2026-10-23

## Context

A portfolio project should demonstrate more than a monolithic demo node. It should also make future hardware integration possible without rewriting application logic.

## Decision

Use typed actions for cancellable missions, Nav2 for path planning/control, robot_localization for sensor fusion, ros2_control for the base boundary, and an independent velocity supervisor between Nav2 and the drive controller.

## Consequences

Individual layers can be unit-tested and replaced. The cost is more package and launch configuration, plus the need to manage topic ownership carefully.
