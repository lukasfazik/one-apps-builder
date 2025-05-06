import subprocess
import json


def get_qemu_image_size_mb(path: str) -> int:
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
        return size

def convert_image_format(input_path: str, output_path: str, output_format: str) -> bool:
    result = subprocess.run(['qemu-img', 'convert', '-O', output_format, input_path, output_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error converting image format: {result.stderr}")
        return False
    return True

