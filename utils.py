# Copyright 2025 Lukáš Fázik
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from one import One
from states import VMLCMState
import logging
import os
import time

loggger = logging.getLogger("main." + __name__)

def calculate_disk_location(disk_target: str) -> int:
    """
    Calculate the disk location based on the target string.
    The target string is expected to be in the format "sdX", where X is a letter.
    """
    loggger.debug(f"Calculating disk location for target: {disk_target}")
    result = ord(disk_target.lower()[2]) - ord("a")
    loggger.debug(f"Disk location calculated: {result}")
    return result

def detach_image_by_id(one: One, vm_id: int, image_id: int) -> bool:
    """
    Detaches all images from the VM that have the corresponding ID.
    :param one: One instance for OpenNebula connection.
    :param vm_id: ID of the VM from which to detach the image.
    :param image_id: ID of the image to detach.
    :return: True if the image was detached successfully, False otherwise.
    """
    loggger.debug(f"Detaching image with ID {image_id} from VM {vm_id}")
    vm_disks = one.get_vm_disks(vm_id)
    if vm_disks is None:
        loggger.error(f"Failed to get VM disks for VM ID {vm_id}")
        return False
    loggger.debug(f"VM has {vm_disks.count} disks")
    for disk in vm_disks:
        if (vm_image_id := disk.get("IMAGE_ID")) and image_id == int(vm_image_id):
            disk_id = int(disk.get("DISK_ID"))
            loggger.debug(f"Trying to detach disk {disk_id} from VM")
            one.wait_for_vm_state(vm_id, VMLCMState.RUNNING)
            if one.detach_vm_image(vm_id, disk_id) is False:
                loggger.error(f"Failed to detach disk {disk_id} from VM {vm_id}")
                return False
    return True

def lock(lock_file_path: str, key: str = "") -> bool:
    """
    Creates a lock using a exclusive file creation.
    :param path: Path to the lock file.
    :return: True if the file was created successfully, False otherwise.
    """
    loggger.debug(f"Creating lock file: {lock_file_path}")
    try:
        with open(lock_file_path, 'x') as f:
            loggger.debug(f"Lock file opened successfully")
            loggger.debug(f"Writing key to lock file, value: {key}")
            f.write(key)
            f.flush()
            loggger.debug(f"Lock file created successfully")
            return True
    except Exception as e:
        loggger.debug(f"Failed to create lock file: {e}")
        return False

def unlock(lock_file_path: str, key: str = "") -> bool:
    """
    Removes a lock by deleting the lock file.
    :param path: Path to the lock file.
    :return: True if the file wasremoved successfully, False otherwise.
    """
    loggger.debug(f"Releasing lock file: {lock_file_path}, key: {key}")
    try:
        with open(lock_file_path, 'r') as f:
            loggger.debug(f"Lock file opened successfully")
            loggger.debug(f"Reading key from lock file")
            file_key = f.read()
            if file_key != key:
                loggger.error(f"Key mismatch: expected: {key}, found: {file_key}")
                return False
        loggger.debug(f"Key matched, removing lock file")
        os.remove(lock_file_path)
        loggger.debug(f"Lock file removed successfully")
        return True
    except Exception as e:
        loggger.warning(f"Failed to remove lock file: {e}")
        return False

def acquire_lock(lock_file_path: str, key: str = "", timeout: int = 300) -> bool:
    """
    Tryies to acquire a lock using the exclusively openned file.
    :param path: Path to the lock file.
    :return: True if the lock was acquired, False otherwise.
    """
    loggger.debug(f"Acquiring lock using file: {lock_file_path} and key: {key}")
    start_time = time.time()
    while True:
        if lock(lock_file_path, key):
            loggger.debug(f"Lock acquired")
            return True
        if time.time() - start_time > timeout:
            loggger.error(f"Failed to acquire lock using file: {lock_file_path}, key: {key} within timeout: {timeout} seconds")
            return False
        time.sleep(1)
