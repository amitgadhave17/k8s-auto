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
apps_v1_api = client.AppsV1Api()
batch_v1_api = client.BatchV1Api()

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

def _safe_get(obj, *keys, default=None):
    cur = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def delete_resources_from_yaml(file_path, default_namespace="default"):
    with open(file_path) as f:
        docs = list(yaml.safe_load_all(f))

    for doc in docs:
        if not isinstance(doc, dict):
            continue

        kind = doc.get("kind")
        name = _safe_get(doc, "metadata", "name")
        namespace = _safe_get(doc, "metadata", "namespace", default=default_namespace) or default_namespace

        if not kind or not name:
            continue

        try:
            if kind == "Pod":
                core_v1_api.delete_namespaced_pod(name=name, namespace=namespace, grace_period_seconds=0)
            elif kind == "Deployment":
                apps_v1_api.delete_namespaced_deployment(name=name, namespace=namespace, propagation_policy="Foreground")
            elif kind == "DaemonSet":
                apps_v1_api.delete_namespaced_daemon_set(name=name, namespace=namespace, propagation_policy="Foreground")
            elif kind == "StatefulSet":
                apps_v1_api.delete_namespaced_stateful_set(name=name, namespace=namespace, propagation_policy="Foreground")
            elif kind == "ReplicaSet":
                apps_v1_api.delete_namespaced_replica_set(name=name, namespace=namespace, propagation_policy="Foreground")
            elif kind == "Job":
                batch_v1_api.delete_namespaced_job(name=name, namespace=namespace, propagation_policy="Foreground")
            elif kind == "CronJob":
                batch_v1_api.delete_namespaced_cron_job(name=name, namespace=namespace, propagation_policy="Foreground")
            elif kind == "Service":
                core_v1_api.delete_namespaced_service(name=name, namespace=namespace)
            elif kind == "ConfigMap":
                core_v1_api.delete_namespaced_config_map(name=name, namespace=namespace)
            elif kind == "Secret":
                core_v1_api.delete_namespaced_secret(name=name, namespace=namespace)
        except client.exceptions.ApiException as e:
            if getattr(e, "status", None) != 404:
                print(f"Failed deleting {kind}/{name} in ns={namespace}: {e}")
        except Exception as e:
            print(f"Failed deleting {kind}/{name} in ns={namespace}: {e}")

def get_pod_name_from_yaml(file_path):
    with open(file_path) as f:
        docs = yaml.safe_load_all(f)
        for doc in docs:
            if doc is not None and doc.get("kind") == "Pod":
                return doc["metadata"]["name"]
    return None

def get_pod_ref_from_yaml(file_path, default_namespace="default"):
    with open(file_path) as f:
        docs = yaml.safe_load_all(f)
        for doc in docs:
            if doc is not None and doc.get("kind") == "Pod":
                name = _safe_get(doc, "metadata", "name")
                namespace = _safe_get(doc, "metadata", "namespace", default=default_namespace) or default_namespace
                if name:
                    return name, namespace
    return None, default_namespace

def wait_for_pod_ready(pod_name, namespace="default", timeout=1000):
    print(f"[{pod_name}] Waiting to be ready...")
    start = time.time()
    while (time.time() - start) < timeout:
        try:
            pod = core_v1_api.read_namespaced_pod(name=pod_name, namespace=namespace)
        except client.exceptions.ApiException as e:
            if getattr(e, "status", None) != 404:
                raise
            time.sleep(1)
            continue

        if pod.status and pod.status.phase == "Running":
            print(f"[{pod_name}] is running.")
            return True

        time.sleep(1)

    print(f"[{pod_name}] Timeout after {timeout} seconds!")
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
    pod_name = None
    pod_namespace = "default"
    try:
        apply_yaml(file_path)
        pod_name, pod_namespace = get_pod_ref_from_yaml(file_path)

        if not pod_name:
            print(f"Could not find pod name in {file_path}, skipping command execution.")
            return

        if wait_for_pod_ready(pod_name, namespace=pod_namespace):
            command = commands_dict.get(pod_name)
            if command:
                run_command_in_pod(pod_name, namespace=pod_namespace, command=command)
            else:
                print(f"[{pod_name}] No command found in JSON, skipping command execution.")
            print(f"[{pod_name}] Sleeping for 10 seconds...")
            time.sleep(20)
        else:
            print(f"[{pod_name}] Not ready before timeout.")
    except Exception as e:
        print(f"Error handling pod {pod_name}: {e}")
    finally:
        delete_resources_from_yaml(file_path)

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
