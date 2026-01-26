import pickle
import argparse
import shutil
import os

def export_model(input_file, output_dir):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # In a real scenario, this might convert the model to ONNX or just copy the pickle
    # For River models, pickle is the standard way.

    dest = os.path.join(output_dir, "model.pkl")
    shutil.copy2(input_file, dest)
    print(f"Model exported to {dest}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input pickle file")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    export_model(args.input, args.output_dir)
