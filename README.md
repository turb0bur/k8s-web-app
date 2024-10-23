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

#### Create ConfigMap and Secrets

Store application configurations (non-sensitive data) in a ConfigMap and sensitive data (e.g., database credentials) in
Secrets

```bash
kubectl -n web-app apply -f k8s/postgres-config.yaml
kubectl -n web-app apply -f k8s/postgres-secret.yaml
kubectl -n web-app apply -f k8s/app-config.yaml
kubectl -n web-app apply -f k8s/app-secret.yaml
``` 

#### Deploy PostgreSQL (StatefulSet)

PostgreSQL is deployed as a StatefulSet for better persistence and stable network identity.

```bash
kubectl -n web-app apply -f k8s/postgres-statefulset.yaml
```

#### Create PostgreSQL Services

- **Headless Service**: For stable DNS and direct pod access
- **ClusterIP Service**: For internal application connections

```bash
kubectl -n web-app apply -f k8s/postgres-headless.yaml 
kubectl -n web-app apply -f k8s/postgres-service.yaml
```

#### Deploy the Python Web Application

Now, deploy the Python app using a Deployment resource:

```bash
kubectl -n web-app apply -f k8s/app-deployment.yaml
```

#### Create a Service for the Application

Expose the Python app using a Service for internal/external access:

```bash
kubectl -n web-app apply -f k8s/app-service.yaml
```

#### Access the Application

In Minikube, you can access the app using the Minikube IP:

```bash
minikube service app-service -n web-app
```

#### Cleanup

To remove the Kubernetes resources, run:

```bash
kubectl delete namespace web-app
```

### Additional Information

- PostgreSQL database tables are created via an init script (init.sql), which is mounted into the PostgreSQL StatefulSet
  via a ConfigMap.
- PostgreSQL StatefulSet uses a Headless Service for stable network identity and a ClusterIP Service for internal
  connections.
- For readiness probes, refer to the Kubernetes manifests for automatic health checks.