#!/usr/bin/env python3
# Collect a CitraVR bugreport from a connected Android device
# Author: Amanda M. Watson (amwatson)

import os
import subprocess as sp
import sys
import argparse

tmpdir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tmp')

# ================
# Helper functions
# ================

def shell_cmd(cmd, verbose=False, show_interium_output=False):
    if verbose:
        print(f"> {cmd}")
    try:
        if show_interium_output:
            return sp.run(cmd, shell=True, stderr=sp.STDOUT, text=True).stdout
        else:
            return sp.check_output(cmd, shell=True, stderr=sp.STDOUT).decode('utf-8')
    except sp.CalledProcessError as e:
        return e.output.decode('utf-8')

# adb binary is located at [path to this file]/bin/[win32|linux|darwin]/adb
def find_adb():
    platform_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bin', sys.platform, 'adb')
    if sys.platform == "win32":
        platform_path += ".exe"
    return platform_path

def select_device_id(devices):
    for device in devices:
        if "device" in device:
            device_id = device.split('\t')[0]
            break
    else:
        return None
    return device_id

def capture_screenshot(adb_path, device_id, file_name):
    shell_cmd(f"{adb_path} -s {device_id} shell screencap -p /sdcard/{file_name}.png")
    shell_cmd(f"{adb_path} -s {device_id} pull /sdcard/{file_name}.png {tmpdir_path}")
    shell_cmd(f"{adb_path} -s {device_id} shell rm /sdcard/{file_name}.png")
    return f"{tmpdir_path}/{file_name}.png"

# Capture the screen until the user presses Ctrl+C, then save the recording to a file
def capture_screenrecord(adb_path, device_id, file_name):
    try:
        print("Press Ctrl+C to stop recording...")
        shell_cmd(f"{adb_path} -s {device_id} shell screenrecord /data/local/tmp/{file_name}.mp4")
    except KeyboardInterrupt:
        print("Screen recording stopped")
    shell_cmd(f"{adb_path} -s {device_id} pull /data/local/tmp/{file_name}.mp4 {tmpdir_path}")
    shell_cmd(f"{adb_path} -s {device_id} shell rm /data/local/tmp/{file_name}.mp4")
    return f"{tmpdir_path}/{file_name}.mp4"

# Citra log dir is a directory on the sdcard containing "citra_log.txt" and/or
# "citra_log.txt.old.txt"
def find_citra_log_dir(adb_path, device_id):
    try:
        citra_log_files = shell_cmd(f"{adb_path} -s {device_id} shell find /sdcard/ -name citra_log.txt 2> /dev/null").split('\n')[:-1]
        return os.path.dirname(citra_log_files[0])
    except Exception as e:
        return None

def get_citra_log(adb_path, device_id, citra_log_dir):
    try:
        shell_cmd(f"{adb_path} -s {device_id} pull {citra_log_dir} {tmpdir_path}/citravr_logs")
        return f"{tmpdir_path}/{os.path.basename(citra_log_dir)}"
    except Exception as e:
        return None

# ================
# Main function
# ================

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Collect CitraVR bugreport from connected Android device")
    parser.add_argument("--screenshot", action="store_true", help="Take a screenshot of the device")
    parser.add_argument("--screenrecord", action="store_true", help="Record the device screen")
    args = parser.parse_args()

    adb_path = find_adb()
    if not os.path.exists(adb_path):
        print(f"Error: adb binary not found for platform {sys.platform} ({adb_path})")
        sys.exit(1)

    # Check that the device is connected (USB or tcpip)
    device_output = shell_cmd(f"{adb_path} devices")
    devices = device_output.split('\n')[1:-1]
    
    if not devices or "device" not in devices[0]:
        print("Error: No device found. Make sure your device is connected.")
        sys.exit(1)

    preferred_device_id = select_device_id(devices)
    if not preferred_device_id:
        print("Error: No device found. Make sure your device is connected.")
        sys.exit(1)

    # Create the tmp directory if it doesn't exist
    os.makedirs(tmpdir_path, exist_ok=True)

    # Capture screenshot
    if args.screenshot:
        screenshot_file = capture_screenshot(adb_path, preferred_device_id, "screenshot")
        print(f"Screenshot saved to {screenshot_file}")
    if args.screenrecord:
        screenrecord_file = capture_screenrecord(adb_path, preferred_device_id, "screenrecord")
        print(f"Screen recording saved to {screenrecord_file}")

    # Find citra log dir
    citra_log_dir = get_citra_log(adb_path, preferred_device_id, find_citra_log_dir(adb_path, preferred_device_id))

    # Collect bugreport
    print("Collecting bugreport...")
    datetime_str = shell_cmd(f"{adb_path} -s {preferred_device_id} shell date +'%Y-%m-%d_%H-%M-%S'").strip()
    bugreport_path =  f"bugreport_{datetime_str}.zip"
    shell_cmd(f"{adb_path} -s {preferred_device_id} bugreport {bugreport_path}", verbose=True, show_interium_output=True)

    # Place any screenshots or screen recordings in the bugreport
    if args.screenshot:
        shell_cmd(f"zip -j {bugreport_path} {screenshot_file}")
    if args.screenrecord:
        shell_cmd(f"zip -j {bugreport_path} {screenrecord_file}")

    # Place citra log dir (if it exists) in the bugreport
    if citra_log_dir:
        shell_cmd(f"zip -r {bugreport_path} {citra_log_dir}")

    # Clean up
    shell_cmd(f"rm -rf {tmpdir_path}")


if __name__ == "__main__":
    main()
