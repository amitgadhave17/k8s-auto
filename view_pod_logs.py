import subprocess
import sys
import time
import argparse
import platform
import math

def get_pods_with_prefix(namespace, prefix):
    """Get all pod names in a namespace that contain the specified prefix."""
    try:
        cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "jsonpath={.items[*].metadata.name}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        all_pods = result.stdout.strip().split()
        filtered_pods = [pod for pod in all_pods if prefix in pod]
        return filtered_pods
    except subprocess.CalledProcessError as e:
        print(f"Error getting pods: {e.stderr}")
        return []

def open_log_window(pod_name, namespace, search_string, use_regex=False, activity_name=None):
    """Open a new terminal window to display logs for a specific pod."""
    os_type = platform.system()
    
    if os_type == "Windows":
        # PowerShell command for Windows with tail/follow
        if activity_name and search_string:
            # Filter by both activity_name and search string
            activity_filter = f"Select-String -Pattern '\"activity_name\":\"[^\"]*{activity_name}[^\"]*\"'"
            if use_regex:
                search_filter = f"Select-String -Pattern '{search_string}'"
            else:
                search_filter = f"Select-String -Pattern '{search_string}' -SimpleMatch"
            ps_command = f"kubectl logs -f {pod_name} -n {namespace} | {activity_filter} | {search_filter}"
        elif activity_name:
            # Filter by activity_name only
            ps_command = f"kubectl logs -f {pod_name} -n {namespace} | Select-String -Pattern '\"activity_name\":\"[^\"]*{activity_name}[^\"]*\"'"
        elif use_regex:
            ps_command = f"kubectl logs -f {pod_name} -n {namespace} | Select-String -Pattern '{search_string}'"
        else:
            ps_command = f"kubectl logs -f {pod_name} -n {namespace} | Select-String -Pattern '{search_string}' -SimpleMatch"
        
        # Build a script that executes the command, stores output, displays it, and waits
        # Build filter display string
        if activity_name and search_string:
            filter_display = f"activity_name={activity_name} AND search={search_string}"
        elif activity_name:
            filter_display = f"activity_name={activity_name}"
        else:
            filter_display = search_string
        
        full_command = f"""
$host.UI.RawUI.WindowTitle = '{pod_name}'

Write-Host 'Tailing logs for pod: {pod_name}' -ForegroundColor Cyan
Write-Host 'Namespace: {namespace}' -ForegroundColor Cyan
Write-Host 'Filter: {filter_display}' -ForegroundColor Cyan
Write-Host '-----------------------------------' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop tailing (window will stay open)' -ForegroundColor Yellow
Write-Host '-----------------------------------' -ForegroundColor Cyan
Write-Host ''

try {{
    {ps_command}
}} catch {{
    Write-Host ''
    Write-Host 'Log tailing stopped' -ForegroundColor Yellow
}}

Write-Host ''
Write-Host 'Tailing stopped. Scroll up to review logs.' -ForegroundColor Green
Write-Host 'Press any key to close window...' -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"""
        
        # Build the command as a list to properly pass to PowerShell
        cmd = [
            "powershell.exe",
            "-NoExit",
            "-NoProfile",
            "-Command",
            full_command
        ]
        
        try:
            # Use CREATE_NEW_CONSOLE to open in a new window
            # This requires running the script with appropriate permissions
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            print(f"Opened log window for pod: {pod_name}")
        except Exception as e:
            print(f"Error opening window for {pod_name}: {e}")
            
    elif os_type == "Darwin":
        # macOS - use Terminal.app via osascript
        if activity_name and search_string:
            # Filter by both activity_name and search string
            activity_filter = f"grep -E '\"activity_name\":\"[^\"]*{activity_name}[^\"]*\"'"
            if use_regex:
                search_filter = f"grep -E '{search_string}'"
            else:
                search_filter = f"grep -F '{search_string}'"
            bash_command = f"kubectl logs -f {pod_name} -n {namespace} | {activity_filter} | {search_filter}"
        elif activity_name:
            # Filter by activity_name only
            bash_command = f"kubectl logs -f {pod_name} -n {namespace} | grep -E '\"activity_name\":\"[^\"]*{activity_name}[^\"]*\"'"
        elif use_regex:
            bash_command = f"kubectl logs -f {pod_name} -n {namespace} | grep -E '{search_string}'"
        else:
            bash_command = f"kubectl logs -f {pod_name} -n {namespace} | grep -F '{search_string}'"
        
        # Build filter display string
        if activity_name and search_string:
            filter_display = f"activity_name={activity_name} AND search={search_string}"
        elif activity_name:
            filter_display = f"activity_name={activity_name}"
        else:
            filter_display = search_string
        
        # Create AppleScript to open new Terminal window
        applescript = f'''
tell application "Terminal"
    do script "echo 'Tailing logs for pod: {pod_name}'; echo 'Namespace: {namespace}'; echo 'Filter: {filter_display}'; echo '-----------------------------------'; echo 'Press Ctrl+C to stop tailing (window will stay open)'; echo '-----------------------------------'; echo ''; {bash_command}; echo ''; echo 'Tailing stopped. Scroll up to review logs.'; read -p 'Press Enter to close window...'"
    set custom title of front window to "{pod_name}"
    activate
end tell
'''
        
        try:
            subprocess.Popen(["osascript", "-e", applescript])
            print(f"Opened log window for pod: {pod_name}")
        except Exception as e:
            print(f"Error opening window for {pod_name}: {e}")
            
    elif os_type == "Linux":
        # Bash command for Linux (using grep for filtering) with tail/follow
        if activity_name and search_string:
            # Filter by both activity_name and search string
            activity_filter = f"grep -E '\"activity_name\":\"[^\"]*{activity_name}[^\"]*\"'"
            if use_regex:
                search_filter = f"grep -E '{search_string}'"
            else:
                search_filter = f"grep -F '{search_string}'"
            bash_command = f"kubectl logs -f {pod_name} -n {namespace} | {activity_filter} | {search_filter}"
        elif activity_name:
            # Filter by activity_name only
            bash_command = f"kubectl logs -f {pod_name} -n {namespace} | grep -E '\"activity_name\":\"[^\"]*{activity_name}[^\"]*\"'"
        elif use_regex:
            bash_command = f"kubectl logs -f {pod_name} -n {namespace} | grep -E '{search_string}'"
        else:
            bash_command = f"kubectl logs -f {pod_name} -n {namespace} | grep -F '{search_string}'"
        
        # Try different terminal emulators in order of preference
        terminals = [
            ["gnome-terminal", "--title", pod_name, "--", "bash", "-c", f"{bash_command}; read -p 'Press Enter to close...'"],
            ["xterm", "-T", pod_name, "-hold", "-e", bash_command],
            ["konsole", "--title", pod_name, "-e", "bash", "-c", f"{bash_command}; read -p 'Press Enter to close...'"],
            ["xfce4-terminal", "--title", pod_name, "-e", f"bash -c '{bash_command}; read -p \"Press Enter to close...\"'"]
        ]
        
        opened = False
        for terminal_cmd in terminals:
            try:
                subprocess.Popen(terminal_cmd)
                print(f"Opened log window for pod: {pod_name}")
                opened = True
                break
            except FileNotFoundError:
                continue
            except Exception as e:
                continue
        
        if not opened:
            print(f"Error: No supported terminal emulator found for {pod_name}")
            print(f"Please install one of: gnome-terminal, xterm, konsole, or xfce4-terminal")
    else:
        print(f"Unsupported operating system: {os_type}")
        print(f"This script supports Windows, macOS, and Linux.")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="View logs from multiple Kubernetes pods in separate terminal windows (Windows, macOS & Linux)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        # Default search (literal string match)
        python view_pod_logs.py -s "launch-ingress-remote-file-copy-tool"
        
        # Regex search
        python view_pod_logs.py -s "error|warning" --regex
        
        # Filter by activity_name in JSON logs
        python view_pod_logs.py -a "Launch"
        python view_pod_logs.py -a "Create"
        python view_pod_logs.py --activity-name "Delete"
        
        # Filter by both activity_name AND search string
        python view_pod_logs.py -a "Launch" -s "file-copy"
        python view_pod_logs.py -a "Create" -s "error|warning" --regex
        
        # Custom namespace and pod prefix
        python view_pod_logs.py -n monitoring -p prometheus -s "scrape_error" --regex

        Platform Support:
        Windows: Uses PowerShell with Select-String
        Linux: Uses grep with gnome-terminal, xterm, konsole, or xfce4-terminal
                """
            )
            
    parser.add_argument(
        "-n", "--namespace",
        default="qualys",
        help="Kubernetes namespace (default: qualys)"
    )
    
    parser.add_argument(
        "-p", "--pod-prefix",
        default="qualys-runtime-sensor",
        help="Pod name prefix to filter (default: qualys-runtime-sensor)"
    )
    
    parser.add_argument(
        "-s", "--search",
        default="launch-ingress-remote-file-copy-tool",
        help="Search string or regex pattern (default: launch-ingress-remote-file-copy-tool)"
    )
    
    parser.add_argument(
        "-r", "--regex",
        action="store_true",
        help="Treat search string as regex pattern (default: literal string match)"
    )
    
    parser.add_argument(
        "-a", "--activity-name",
        help="Filter by activity_name field in JSON logs (e.g., Launch, Create, Update, Delete). Can be combined with -s/--search."
    )
    
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=0.5,
        help="Delay in seconds between opening windows (default: 0.5)"
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    print(f"Retrieving pods with prefix '{args.pod_prefix}' from namespace '{args.namespace}'...")
    pods = get_pods_with_prefix(args.namespace, args.pod_prefix)
    
    if not pods:
        print(f"No pods found with prefix '{args.pod_prefix}' in namespace '{args.namespace}'")
        return
    
    print(f"Found {len(pods)} pod(s):")
    for pod in pods:
        print(f"  - {pod}")
    
    if args.activity_name and args.search:
        search_type = "regex pattern" if args.regex else "literal string"
        print(f"\nOpening log windows filtering by activity_name: '{args.activity_name}' AND {search_type}: '{args.search}'...")
    elif args.activity_name:
        print(f"\nOpening log windows filtering by activity_name: '{args.activity_name}'...")
    else:
        search_type = "regex pattern" if args.regex else "literal string"
        print(f"\nOpening log windows with {search_type}: '{args.search}'...")
    
    print(f"\nOpening {len(pods)} log window(s)...")
    
    for pod in pods:
        open_log_window(pod, args.namespace, args.search, args.regex, args.activity_name)
        time.sleep(args.delay)
    
    print(f"\nOpened {len(pods)} log window(s)")

if __name__ == "__main__":
    main()
