import subprocess
import json


def get_qemu_image_size_mb(path: str) -> int:
    """
    Get the size of a QEMU image in MB using qemu-img. Does not work for images less than 1MB in size.
    :param path: Path to the QEMU image file.
    :return: Size of the image in MB, or -1 if an error occurs.
    """
    result = subprocess.run(['qemu-img', 'info', '--output', 'json', path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error getting image size: {result.stderr}")
        return -1
    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output from qemu-img: {e}")
        return -1
    size = info.get("virtual-size", -1)
    if size == -1:
        print("Error: 'virtual-size' not found in qemu-img output.")
        return -1
    return size // (1024**2)


def convert_image_format(input_path: str, output_path: str, output_format: str) -> bool:
    """
    Convert a QEMU image to a different format using qemu-img.
    :param input_path: Path to the input QEMU image file.
    :param output_path: Path to the output QEMU image file.
    :param output_format: Desired output format (e.g., 'qcow2', 'raw').
    :return: True if conversion is successful, False otherwise.
    """
    print(f"Converting image from {input_path} to {output_path} with format {output_format}")
    result = subprocess.run(['qemu-img', 'convert', '-O', output_format, input_path, output_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error converting image format: {result.stderr}")
        return False
    print(f"Image converted successfully")
    return True
