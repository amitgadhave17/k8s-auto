FROM ubuntu:20.04

# Suppress tzdata prompt
ENV DEBIAN_FRONTEND=noninteractive

# Install traditional netcat (not OpenBSD)
RUN apt update && \
	apt install -y netcat-traditional && \
	ln -sf /bin/nc.traditional /bin/nc && \
	apt clean
	
#install pnscan - network scanning
RUN apt install pnscan -y

# Install required packages and Docker CLI
RUN apt-get update && apt-get install -y \
	ca-certificates \
	curl \
	gnupg \
	lsb-release

# Add Docker’s official GPG key
RUN mkdir -p /etc/apt/keyrings && \
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the Docker repository
RUN echo \
	"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
	$(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker CLI only (without Docker engine)
RUN apt-get update && apt-get install -y docker-ce-cli

#install steghide
RUN apt-get install steghide -y

#install compiler
RUN apt-get install build-essential -y

#install kubectl
RUN curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
RUN echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list
RUN  apt-get update
RUN apt-get install -y kubectl

#install tcpdump
RUN apt-get install -y tcpdump


#install python
RUN apt-get install -y python3

#install gdb
RUN apt-get install -y gdb

#install kmod
RUN apt-get install -y kmod

#install cron
RUN apt-get install -y cron

#install vim
RUN apt-get install -y vim

#install ssh
RUN apt-get install -y ssh openssh-client

#build program
COPY memfd-exec.c .
RUN gcc -o memfd-exec memfd-exec.c
RUN chmod +x memfd-exec

RUN useradd test
# Optional: default to bash shell on reverse connect (override with CMD)
CMD ["sleep", "infinity"]

