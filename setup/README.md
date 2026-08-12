# Initial setup tools

Run these commands from the repository root.

1. Install the project into its own virtual environment:

   ```sh
   ./setup/install.sh
   . .venv/bin/activate
   ```

2. On Linux, give your user serial-port access, then log out and back in:

   ```sh
   sudo usermod -aG dialout "$USER"
   ```

3. Assign servo IDs one at a time. **Only one servo may be connected** while
   changing an ID:

   ```sh
   python setup/set_servo_id.py --old-id 1 --new-id 5 --yes
   ```

   This example changes ID 1 to ID 5; substitute the IDs required by the
   matching joint in `config/spider.toml`.

4. Connect the complete bus and perform a read-only check:

   ```sh
   python setup/check_servos.py
   ```

5. Tune joint neutrals, directions, and limits in `config/spider.toml` while
   the chassis is supported above the floor. Follow `docs/setup.md` before the
   first powered movement.


