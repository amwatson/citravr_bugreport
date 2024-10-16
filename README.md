# Compatibility
This script is compatible with the following platforms:

- Windows
- macOS (OSX)
- Linux: the included adb binary should work on common Linux distributions such as Ubuntu and Fedora, but specific configurations may vary.

# Instructions

To collect a bug report from a connected Quest HMD, run the following command:

```bash
python3 collect_bugreport.py
```

> **Note:** If you are on Windows and you encounter the error:
> 
> ```
> Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases.
> ```
> This is caused by a Windows feature that intercepts certain commands. To fix this:
> 1. Open the **Start Menu**, search for **App Execution Aliases**, and click on it.
> 2. In the **App Execution Aliases** window, scroll down to the `python.exe` and `python3.exe` entries.
> 3. Turn off both toggles for `python.exe` and `python3.exe` to prevent Windows from redirecting you to the Microsoft Store.
> 4. Ensure Python is installed on your system by running `python --version` or `python3 --version`.

## Options

- `--screenshot`: Attaches a screenshot of the device screen, taken just before the bug report is captured. This is helpful for showing the graphics impact of a bug, when possible.

  Example:
  ```bash
  python3 collect_bugreport.py --screenshot
  ```

- `--screenrecord`: Creates a video recording of the device screen before capturing the bug report. This is helpful for showing how an issue is reproduced, when possible.

  Example:
  ```bash
  python3 collect_bugreport.py --screenrecord
  ```

## Additional Notes
- Ensure that a device is connected either via USB or over the network using `adb connect` before running the script.
