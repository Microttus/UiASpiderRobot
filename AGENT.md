# Agent Instructions

## Project scope

This repository contains an IsaacLab-based reinforcement-learning environment for robotic battery disassembly.

The primary task uses a Franka Panda robot to perform a staged disassembly sequence:

1. Approach and grasp the locking pin.
2. Remove the pin from the assembly.
3. Move the pin aside and release it.
4. Approach and grasp the center handle.
5. Extract the center and move it toward the target.

The project uses:

- Isaac Sim and IsaacLab.
- `ManagerBasedRLEnvCfg`.
- Differential inverse kinematics for arm control.
- Binary open/close gripper actions.
- Stable-Baselines3 PPO for primary training.
- Thousands of parallel GPU environments.
- Custom reward, observation, event, and termination functions.
- Long-running experiments where comparability between runs matters.

Experimental continuity is a project requirement. Prefer preserving a working baseline over redesigning the task.

---

## Important project locations

The primary task implementation is under:

```text
source/RoboticBatteryDisassembly/RoboticBatteryDisassembly/
tasks/battery_lab/franka_cylinder/