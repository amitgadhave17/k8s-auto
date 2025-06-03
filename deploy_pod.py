import os
import time
import yaml
import json
import argparse
from concurrent.futures import ThreadPoolExecutor
from kubernetes import client, config, utils
from kubernetes.stream import stream

# Load kubeconfig
config.load_kube_config()

# Kubernetes API clients
api_client = client.ApiClient()
core_v1_api = client.CoreV1Api()

# JSON file with commands
commands_json_path = "./commands.json"

# Load commands from JSON
with open(commands_json_path, 'r') as f:
    commands_dict = json.load(f)

def apply_yaml(file_path):
    with open(file_path) as f:
        docs = yaml.safe_load_all(f)
        for doc in docs:
            if doc is not None:
                utils.create_from_dict(api_client, data=doc)

def get_pod_name_from_yaml(file_path):
    with open(file_path) as f:
        docs = yaml.safe_load_all(f)
        for doc in docs:
            if doc is not None and doc.get("kind") == "Pod":
                return doc["metadata"]["name"]
    return None

def wait_for_pod_ready(pod_name, namespace="default", timeout=1000):
    print(f"[{pod_name}] Waiting to be ready...")
    #for _ in range(timeout):
    while True: 
    # Infinite loop to keep checking the pod status 
        pod = core_v1_api.read_namespaced_pod(name=pod_name, namespace=namespace)
        if pod.status.phase == "Running":
            print(f"[{pod_name}] is running.")
            return True
        time.sleep(1)
    print(f"[{pod_name}] Timeout!")
    return False

def run_command_in_pod(pod_name, namespace="default", command=None):
    print(f"[{pod_name}] Running command inside...")
    resp = stream(
        core_v1_api.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=command,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
    )
    print(f"[{pod_name}] Command output:\n{resp}")

def delete_pod(pod_name, namespace="default"):
    print(f"[{pod_name}] Deleting pod...")
    core_v1_api.delete_namespaced_pod(name=pod_name, namespace=namespace)

def deploy_and_run(file_path):
    pod_name = get_pod_name_from_yaml(file_path)
    if not pod_name:
        print(f"Could not find pod name in {file_path}, skipping...")
        return

    try:
        apply_yaml(file_path)
        if wait_for_pod_ready(pod_name):
            command = commands_dict.get(pod_name)
            if command:
                run_command_in_pod(pod_name, command=command)
            else:
                print(f"[{pod_name}] No command found in JSON, skipping command execution.")
            print(f"[{pod_name}] Sleeping for 10 seconds...")
            time.sleep(20)
            delete_pod(pod_name)
        else:
            print(f"[{pod_name}] Not ready, skipping delete.")
    except Exception as e:
        print(f"Error handling pod {pod_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Deploy YAML(s) to Kubernetes and run commands.")
    parser.add_argument(
        "path",
        nargs="?",  # optional
        default="./yamls",
        help="Path to YAML file or folder (default: ./yamls)"
    )
    args = parser.parse_args()

    yaml_files = []

    if os.path.isfile(args.path):
        yaml_files.append(args.path)
    elif os.path.isdir(args.path):
        for filename in os.listdir(args.path):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                yaml_files.append(os.path.join(args.path, filename))
    else:
        print(f"Invalid path: {args.path}")
        return

    if not yaml_files:
        print("No YAML files found.")
        return

    print(f"Found {len(yaml_files)} YAML file(s) to deploy.")

    with ThreadPoolExecutor(max_workers=len(yaml_files)) as executor:
        executor.map(deploy_and_run, yaml_files)

if __name__ == "__main__":
    main()
