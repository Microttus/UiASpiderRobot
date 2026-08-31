# UiA Spider Robot

Control software for the UiA spider robot with 8 legs.

## Features

- Support for multiple gaits:
  - Alternating Tetrapod Gait (default)
  - Ripple Gait (newly added)
  - Tripod Gait (newly added)

## Usage

The robot can be controlled using the `spider-robot` command-line tool.

### Basic Commands

```bash
# Stand up
spider-robot stand

# Sit down
spider-robot sit

# Storage position
spider-robot storage

# Walk forward
spider-robot walk forward

# Walk in a specific direction
spider-robot walk left
spider-robot walk turn-left
```

### Gait Selection

You can select which gait to use with the `--gait` flag:

```bash
# Use the default alternating tetrapod gait (default)
spider-robot --gait alternating_tetrapod walk forward

# Use the ripple gait
spider-robot --gait ripple walk forward

# Use the tripod gait
spider-robot --gait tripod walk forward
```

### Simulation Mode

To test commands without hardware, use simulation mode:

```bash
spider-robot --simulate --gait tripod walk forward
```