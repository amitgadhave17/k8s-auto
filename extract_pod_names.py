import os
import yaml
import argparse

def extract_info_from_file(file_path):
    with open(file_path, 'r') as f:
        try:
            docs = list(yaml.safe_load_all(f))
        except yaml.YAMLError as e:
            print(f"Failed to parse {file_path}: {e}")
            return

        for doc in docs:
            if not doc or doc.get('kind') != 'Pod':
                continue

            containers = doc.get('spec', {}).get('containers', [])
            for container in containers:
                name = container.get('name', 'N/A')
                args = container.get('args', [])
                arg2 = args[1] if len(args) > 1 else "N/A"
                print(f"{os.path.basename(file_path)}: container={name}, arg2={arg2}")
                return os.path.basename(file_path), name, arg2

def main():
    parser = argparse.ArgumentParser(description="Extract container name and 2nd args from Pod YAMLs.")
    parser.add_argument(
        "folder",
        nargs="?",
        default="yamls",
        help="Folder containing YAML files (default: yamls)"
    )
    args = parser.parse_args()

    folder = args.folder

    if not os.path.isdir(folder):
        print(f"Folder '{folder}' does not exist.")
        return

    for filename in os.listdir(folder):
        if filename.endswith((".yaml", ".yml")):
            details= extract_info_from_file(os.path.join(folder, filename))
            if details:
                file_name, container_name, arg2 = details
                #add the header to the csv file
                if not os.path.isfile("rule-pod-name-mapping.csv"):
                    with open("rule-pod-name-mapping.csv", "w") as f:
                        f.write("file_name,container_name,command\n")
                file_name = file_name.replace(".yaml", "").replace(".yml", "")
                with open("rule-pod-name-mapping.csv", "a") as f:
                    f.write(f"{file_name},{container_name},{arg2}\n")

if __name__ == "__main__":
    main()
