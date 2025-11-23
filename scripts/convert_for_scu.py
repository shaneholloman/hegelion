import json
import sys


def convert_hegelion_to_scu(input_file, output_file):
    """
    Converts Hegelion's dialectical JSONL to SCU-compatible JSONL.
    SCU expects {"text": "..."}.
    We will format the text as a ChatML-style or Standard-style interaction.
    """
    print(f"Converting {input_file} -> {output_file}")

    count = 0
    with open(input_file, "r") as fin, open(output_file, "w") as fout:
        for line in fin:
            if not line.strip():
                continue
            try:
                data = json.loads(line)

                # Extract fields
                system = data.get("system", "You are a dialectical reasoning engine.")
                instruction = data.get("instruction", "")
                output = data.get("output", "")

                # Format as text
                # Using a standard chat format
                text = f"<|im_start|>system\n{system}<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>\n"

                # Write SCU format
                json.dump({"text": text}, fout)
                fout.write("\n")
                count += 1
            except Exception as e:
                print(f"Skipping line due to error: {e}")

    print(f"Converted {count} examples.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_data.py <input_jsonl> <output_jsonl>")
        sys.exit(1)

    convert_hegelion_to_scu(sys.argv[1], sys.argv[2])
