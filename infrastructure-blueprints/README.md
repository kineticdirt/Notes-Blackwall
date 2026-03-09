# Infrastructure Blueprints

IaC templates for deploying Cequence BlackWall services across environments.

## Structure

```
infrastructure-blueprints/
├── terraform/
│   ├── modules/              # Reusable per-service modules
│   │   ├── blackwall-service/
│   │   ├── workflow-canvas/
│   │   └── api-gateway/
│   └── environments/         # Environment-specific compositions
│       ├── dev/
│       ├── staging/
│       └── prod/
├── docker/
│   └── docker-compose.yml    # Local full-stack dev environment
└── k8s/
    ├── base/                 # Shared manifests (Kustomize base)
    └── overlays/
        ├── dev/
        └── prod/
```

## Quick Start

### Local (Docker Compose)

```bash
cd docker
docker compose up -d
```

Services exposed:

| Service              | Port  |
|----------------------|-------|
| BlackWall API        | 8000  |
| Workflow Canvas      | 8080  |
| API Gateway          | 9000  |
| Prometheus           | 9090  |
| Grafana              | 3000  |

### Terraform (AWS)

```bash
cd terraform/environments/dev
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

### Kubernetes (Kustomize)

```bash
kubectl apply -k k8s/overlays/dev
```

## Design Principles

- **Environment parity**: dev, staging, and prod share the same modules; only variables differ.
- **Least privilege**: IAM roles scoped per service; no shared credentials.
- **Immutable deploys**: Container images tagged by SHA; no `:latest` in prod.
- **Secrets via vault**: No secrets in code; reference SSM Parameter Store or Secrets Manager.
