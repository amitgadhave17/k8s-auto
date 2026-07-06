# Deprecated YAMLs from 0.9.12_experimental

These YAMLs were moved to the deprecated folder because they **do not have corresponding rules** in the current rule set.

## Moved Files (6 total):

1. **basic-interactive-reconnaissance.yaml**
   - No matching rule found

2. **exploit-log4j-vulnerability-cve-2021-44832.yaml**
   - No matching rule found
   - Note: There is an `Exploit_Log4j_Vulnerability_CVE_2021_44832_T1190` rule in monitored_processes_only.txt but it's NOT in the provided rule list

3. **launch-ingress-remote-file-copy-tools-in-container.yaml**
   - No matching rule found
   - Note: Similar to `Launch_Remote_File_Copy_Tools_In_Container_T1021` but specifically for ingress

4. **ssh-process-launched-from-inside-a-container.yaml**
   - No matching rule found
   - Note: There is an `SSH_Process_Launched_From_Inside_A_Container_T1021_004` rule in monitored_processes_only.txt but it's NOT in the provided rule list

5. **web-server-spawned-shell.yaml**
   - No matching rule found
   - Note: There is a `Web_Server_Spawned_Shell_T1505_003` rule in monitored_processes_only.txt but it's NOT in the provided rule list

6. **web-server-spawned-suspicious-child-process.yaml**
   - No matching rule found
   - Note: There is a `Web_Server_Spawned_Suspicious_Child_Process_T1059` rule in monitored_processes_only.txt but it's NOT in the provided rule list

## Date Moved
July 6, 2026

## Remaining Active YAMLs in 0.9.12_experimental
33 YAMLs remain in the 0.9.12_experimental folder, all with matching rules.

## Missing Rule (YAML needed)
- **GoLang_SSH_GSSAPI_Memory_Exhaustion_CVE_2025_58181_T1499** - This rule exists but has no corresponding YAML file
