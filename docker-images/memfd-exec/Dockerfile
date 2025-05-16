# Stage 1: Build the C binary
FROM gcc:latest AS builder
WORKDIR /app
COPY memfd-exec.c .
RUN gcc -static -o memfd-exec memfd-exec.c


# Stage 2: Runtime container
FROM ubuntu:latest
WORKDIR /app
COPY --from=builder /app/memfd-exec .
COPY --from=builder /app/memfd-exec.c .
# ✅ Make the binary executable
RUN chmod +x /app/memfd-exec

# Run it
CMD ["sh", "-c", "./memfd-exec; sleep infinity"]
