# Resource Manager for Kubernetes

PEMA is a resource manager on top of kubernetes that optimizes resources of microservice applications. 
The resource manager works on on-prem kubernetes cluster. Support for managed kubernetes cluster (AWS EKS, GCP) will be added soon.

### Installing a Kubernetes cluster
Follow instruction at [kubernetes-setup.md](kubernetes-setup.MD)

### Deploy metrics and observability
The prometheus and grafana configuration files are in [here](metric_deployments/prometheus_deployment)

The observability will be installed in `kube-system` namespace

In the master node,
```bash
kubectl apply -f metric_deployments/prometheus_deployment
kubectl get pods -n kube-system 
```

### Deploy application 

### Start the resource manager 

