# Install Full Kubernetes Cluster 

### All nodes
Apply these in all nodes of the cluster. 

Set hostnames of each machines with ip in /etc/hosts 
```bash
sudo vim /etc/hosts

192.168.x.x server1
```

Install docker
```bash
# remove currently installed docker and install docker from official repository
sudo apt remove docker docker-engine docker.io containerd runc
sudo apt update
sudo apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
sudo docker run hello-world
sudo docker --version

# install docker compose
sudo apt remove docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

Install Kubernetes components from script	
```bash
sudo apt install apt-transport-https curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
kubectl version --client && kubeadm version
```

If firewall is active, allow kubernetes ports from this - [Link](https://kubernetes.io/docs/reference/ports-and-protocols/)

```bash
Sudo ufw allow   
```

Disable and delete docker0 network created by docker by default – Kubernetes will install its own 
```bash
sudo /sbin/ifconfig docker0 down 
sudo ip link del docker0 
```

Disable all other pod networks if installed previously – flannel.1, cni0 etc 

Disable swap in /etc/fstab file by commenting the swap entry and live with 
```bash
sudo swapoff -a 
```

enable port forwarding by editing /etc/sysctl.conf and uncomment “net.ipv4.ip_forward=1” 

Need to install pod networks – allow network specific ports. For example, calico use port 179 for communication. Allow this port. Flannel may use different ports.

### On Master Node 

initiate cluster with calico networking [hard way] 

```bash
sudo kubeadm init –pod-network-cidr=10.96.0.0/16 –service-cidr=10.97.0.0/16 –apiserver-advertise-address=192.168.2.12 
```

`192.168.2.12 is the node ip` 

For multi ethernet port servers, find default gateway and provide its ip. Pod networks tends to work with default ethernet port.  

Follow the output of the above command for creating and giving permission of config files 

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

**Take a note of the “kubeadm join” command provided by the init output. We will need this for nodes to join the cluster**

Install a pod network – Kubernetes use internal network called CNI for pod-to-pod networking 

I used calico, downloaded the manifests file by 

`curl https://docs.projectcalico.org/manifests/calico.yaml -O`

install this by `kubectl apply -f calico.yaml`

### Master with weave pod networking (simple) 

The weave networking is downloaded and saved as `weave-daemonset-k8s-1.9.yaml`
```bash
sudo kubeadm init 

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl apply -f “weave-daemonset-k8s-1.9.yaml
```

### Worker Nodes 

use the provided join command from master node. Command is like this 

`sudo kubeadm join <master-ip:port> --token <token> --discovery-token-ca-cert-hash <hash>`

**Repeat for all worker nodes**

## Verify cluster status
### On Master Node 

Verify node join by going to master node and `kubectl get nodes`

Verify all the pods are running by `kubectl get pods –all-namespaces -o wide`

If something is not running or gives error, check details by 

```bash
kubectl describe pod <pod-name> -n kube-system 
kubectl logs <pod-name> -n kube-system 
```

## Install Lightweight (K3S) Kubernetes Cluster
To learn more about lightweight kubernetes (k3s), follow this [https://k3s.io/](https://k3s.io/)
- Follow all steps for **All Nodes** mentioned above

In master node, install the kubernetes server process
```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server" sh -s - --token 12345
sudo chmod 644 /etc/rancher/k3s/k3s.yaml 
```

In worker nodes, install the worker process
```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent --server https://server1:6443 --token 12345" sh -s -
```

Finally, verify cluster statuses. 

## Tear Down a cluster 

From the master, delete the node by 
```bash
sudo kubectl drain <servername> 
sudo kubectl delete node <servername> 
sudo kubeadm reset
```
By following the output, clear settings

- Delete the config directory “.kube/”
- Delete networks settings “/etc/cni/net.d”
- Delete networks created by Kubernetes 

Its better to reset iptables  

In worker node, reset settings 

```bash
sudo kubeadm reset
```

Follow the output for clearing settings
- Delete /etc/cni/net.d
- Delete networks created by Kubernetes – kubeadm won’t delete network by itself

## Possible Issues

#### calico bird is not ready bgp not established with  

This error throws if there’s conflict with docker0 network. 
- Delete both docker0 and a br-xx network. Calico node should up automatically. 	 

#### Dns not working from pod 

Test dns services

Download and deploy `dnsutils.yaml`
``` 
kubectl apply -f dnsutils.yaml
kubectl exec dnsutils – nslookup Kubernetes.default
```

If nothing return or return error follow the steps in this page
[Link](https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/)

In one case, the output was **connection time out, no server could be reached**

The culprit was **dnsmasq**. It changed the /etc/resolv.conf entry to **nameservers 127.0.0.1** but originally it should be **127.0.0.53**

I uninstalled the dnsmasq and restarted the server.

Add resolve-conf to kubelet 
```bash
sudo vim /var/lib/kubelet/kubeadm-flags.env 
sudo systemctl daemon-reload 
sudo service kubelet restart 
```

#### It seems like the kubelet isn't running or healthy. 
Follow this link - 
https://stackoverflow.com/questions/52119985/kubeadm-init-shows-kubelet-isnt-running-or-healthy 

 