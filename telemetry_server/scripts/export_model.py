import argparse
import os


def export_model(input_file, output_dir):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Encrypt the model before exporting to prevent unauthorized use
    from cryptography.fernet import Fernet

    # Same key as in idm_logger/utils/crypto.py
    COMMUNITY_KEY = b"gR6xZ9jK3q2L5n8P7s4v1t0wY_mH-cJdKbNxVfZlQqA="

    f = Fernet(COMMUNITY_KEY)

    with open(input_file, "rb") as file:
        file_data = file.read()

    encrypted_data = f.encrypt(file_data)

    dest = os.path.join(output_dir, "model.enc")
    with open(dest, "wb") as file:
        file.write(encrypted_data)

    print(f"Model encrypted and exported to {dest}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input pickle file")
    parser.add_argument(
        "--output-dir", type=str, required=True, help="Output directory"
    )
    args = parser.parse_args()

    export_model(args.input, args.output_dir)
