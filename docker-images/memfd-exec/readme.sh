
#commands
kubectl delete pod memfd-exec 
docker build -t memfd-exec:latest .
docker tag memfd-exec:latest angelrita/memfd-exec:latest
docker push  angelrita/memfd-exec:latest
kubectl apply -f memfd-exec.yaml
kubectl exec -it memfd-exec -- sh
