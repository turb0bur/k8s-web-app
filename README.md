# Python Web Application with PostgreSQL

This repository contains a Python web application running on PostgreSQL, and it can be run either locally using Docker
Compose or on Kubernetes for a more scalable solution.

## Prerequisites

- [Docker](https://www.docker.com/get-started) installed for local development.
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) or a Kubernetes cluster for Kubernetes deployment.
- [kubectl](https://kubernetes.io/docs/tasks/tools/) CLI to interact with your Kubernetes cluster.

---

## Local Development (Docker Compose)

### Setup

You can run the entire stack locally using Docker Compose, which includes the Python web app and PostgreSQL.

#### Create an `.env` file:

Copy the example environment file and fill in necessary values:

```bash
cp .env.example .env
```

#### Run the application with Docker Compose:

Execute the following command to build and run the application:

```bash
docker-compose up --build
```

#### Access the App:

Once the services are running, you can access the app at `http://localhost:5000`

#### Stopping the Application:

When you're done, stop the running containers with:

```bash
docker-compose down
```

## Minikube Setup

### Starting Minikube with 2 Worker Nodes

Minikube allows you to set up a local Kubernetes cluster for testing and development purposes.

#### Start Minikube

Start Minikube with a default node using:

```bash
minikube start
```

#### Add Worker Nodes

To add two worker nodes, you need to run the following commands:

```bash
minikube node add
minikube node add
```

This will add two extra worker nodes to your Minikube cluster, which you can verify using:

```bash
minikube status
#or
kubectl get nodes
```

#### Access the Kubernetes Dashboard

You can open the Kubernetes dashboard in your browser with:

```bash
minikube dashboard
```

#### Run the Application

After starting Minikube, follow the steps in the [Deployment on Kubernetes](#deployment-on-kubernetes) section to deploy
your application.

### Stopping Minikube

When you are done with the local Kubernetes environment, stop and delete the Minikube cluster:

```bash
minikube stop
minikube delete
```

## Deployment on Kubernetes

### Setup

This section covers deploying the app on a Kubernetes cluster, using StatefulSets for PostgreSQL.

### Steps to Deploy

#### Create a Namespace

You should deploy all resources into a dedicated namespace.

```bash
kubectl create namespace web-app
```

#### Initial Deployment via Helm

```bash
helm install -n web-app python-app ./helm
``` 

#### Deploy Green Deployment:

```bash
helm upgrade -n web-app python-app ./helm --reuse-values --set app.greenDeployment.image.tag=<NEW_IMAGE_TAG> \
--set app.greenDeployment.replicas=2
```

#### Deploy fully tested on the Green Deployment Docker image to the Blue one:

```bash
helm upgrade -n web-app python-app ./helm  --reuse-values --set app.blueDeployment.image.tag=<NEW_IMAGE_TAG> \
--set app.blueDeployment.replicas=2 
```

#### Remove the Green pods:

```bash
helm upgrade -n web-app python-app ./helm  --reuse-values --set app.greenDeployment.replicas=0 
```


#### Access both deployment of the Application

In Minikube, you can access the app using the Minikube IP. 
Please do it in a separate terminal windows.

```bash
minikube service app-service-green -n web-app
minikube service app-service-blue -n web-app
```

#### Cleanup

To remove the Kubernetes resources, run:

```bash
helm uninstall -n web-app python-app
kubectl delete namespace web-app
```

### Additional Information

- PostgreSQL database tables are created via an init script (init.sql), which is mounted into the PostgreSQL StatefulSet
  via a ConfigMap.
- PostgreSQL StatefulSet uses a Headless Service for stable network identity and a ClusterIP Service for internal
  connections.
- For readiness probes, refer to the Kubernetes manifests for automatic health checks.