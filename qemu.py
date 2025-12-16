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

import subprocess
import json
import logging

logger = logging.getLogger("main." + __name__)

def get_qemu_image_size_mb(path: str) -> int:
    """
    Get the size of a QEMU image in MB using qemu-img. Does not work for images less than 1MB in size.
    :param path: Path to the QEMU image file.
    :return: Size of the image in MB, or -1 if an error occurs.
    """
    logger.debug(f"Getting size of QEMU image, path: {path}")
    qemu_img_command = ['qemu-img', 'info', '--output', 'json', path]
    logger.debug(f"Command: {" ".join(qemu_img_command)}")
    result = subprocess.run(qemu_img_command, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"qemu-img exited with error: {result.stderr}")
        return -1
    try:
        logger.debug(f"Parsing JSON qemu-img output: {result.stdout}")
        info = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        logger.error(f"Unable to parse JSON qemu-img output: {e}")
        return -1
    logger.debug(f"Getting virtual size from parsed qemu-img JSON output")
    size = info.get("virtual-size", -1)
    if size == -1:
        logger.error("'virtual-size' not found in qemu-img output.")
        return -1
    result = size // (1024**2)
    logger.debug(f"QEMU image size is {result} MB")
    return result


def convert_image_format(input_path: str, output_path: str, output_format: str) -> bool:
    """
    Convert a QEMU image to a different format using qemu-img.
    :param input_path: Path to the input QEMU image file.
    :param output_path: Path to the output QEMU image file.
    :param output_format: Desired output format (e.g., 'qcow2', 'raw').
    :return: True if conversion is successful, False otherwise.
    """
    logger.debug(f"Converting image from {input_path} to {output_path} with format {output_format}")
    qemu_img_command = ['qemu-img', 'convert', '-O', output_format, input_path, output_path]
    logger.debug(f"Command: {" ".join(qemu_img_command)}")
    result = subprocess.run(qemu_img_command, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"qemu-img failed: {result.stderr}")
        return False
    logger.debug(f"Image converted successfully")
    return True
