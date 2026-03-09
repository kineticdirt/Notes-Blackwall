# DevOps & Ops Reference

Reference for DevOps flow, ops scripting, distributed-systems testing, AWS services, and orchestration/load-balancing concepts. #devops #ops #aws #reference

---

## 1. DevOps flow and terms

**DevOps** = culture and practices that tie **development** and **operations** together so you can ship and run software quickly and reliably.

### The flow (high level)

1. **Plan** — What to build (backlog, epics, stories).
2. **Code** — Write and review code (Git, branches, PRs).
3. **Build** — Turn code into runnable artifacts (compile, package, container images).
4. **Test** — Automated tests (unit, integration, e2e).
5. **Release / Deploy** — Put builds into environments (staging, production).
6. **Operate** — Run and monitor the app (logs, metrics, alerts).
7. **Monitor & Learn** — Use feedback to improve (incidents, performance, usage).

Often drawn as a loop: Plan → Code → Build → Test → Release → Operate → Monitor → back to Plan.

### Core terms

| Term | Meaning |
|------|--------|
| **CI (Continuous Integration)** | Every commit triggers an automated build and tests. "Does this code still work when merged?" |
| **CD (Continuous Delivery)** | Every passing build is *ready* to go to production; release is a business decision. |
| **CD (Continuous Deployment)** | Every passing build is *automatically* deployed to production (no manual "release" step). |
| **Pipeline** | Automated sequence: build → test → (optional) deploy. Defined in YAML (e.g. GitHub Actions, GitLab CI) or in a tool (Jenkins, etc.). |
| **Artifact** | Output of a build (e.g. JAR, Docker image, tarball) that gets deployed. |
| **Environment** | A place the app runs: dev, staging (pre-prod), production. |
| **Infrastructure as Code (IaC)** | Servers, networks, config described in code (Terraform, Ansible, CloudFormation, etc.) and applied by automation. |
| **Orchestration** | How you run and manage containers/services (e.g. Kubernetes, ECS). |
| **Observability** | Logs, metrics, traces (and sometimes alerts) so you can see how the system behaves. |

---

## 2. Ops scripting terms

| Term | Meaning |
|------|--------|
| **Idempotent** | Running the script again gives the same result; safe to re-run (e.g. "create dir if missing", "ensure user exists"). |
| **Declarative vs imperative** | Declarative = describe desired state (Terraform, Ansible). Imperative = list steps to run (bash, Python). |
| **Shell / Bash** | Common for one-off automation, cron jobs, container entrypoints. |
| **Orchestration scripts** | Scripts that call APIs/tools to coordinate services (start order, health checks, rollback). |
| **Cron / scheduler** | Time-based runs (e.g. daily backups, cleanup). In cloud: EventBridge, Cloud Scheduler, etc. |
| **Exit codes** | `0` = success, non-zero = failure. Scripts and pipelines use these to decide pass/fail. |
| **Idempotency key** | Unique key per "logical operation" so retries don't double-apply (important in distributed systems). |

---

## 3. Testing distributed systems

| Term | Meaning |
|------|--------|
| **Contract testing** | Services agree on request/response shapes (e.g. Pact). Test each service against the contract without running all services. |
| **Chaos engineering** | Intentionally break things (kill pods, network partitions, latency) to see how the system behaves. |
| **Integration test** | Test two or more components together (e.g. app + DB, service A + service B). |
| **End-to-end (e2e)** | Test a full path as a user or client would (often against a real or staging environment). |
| **Fake / stub / mock** | **Fake** = real behavior, simplified (e.g. in-memory DB). **Stub** = fixed responses. **Mock** = record expectations and verify calls. |
| **Eventual consistency** | In distributed systems, data may be temporarily inconsistent; tests often need to "wait until" or poll. |
| **Flaky test** | Passes or fails randomly (timing, shared state, network). Fix by making tests deterministic and isolated. |

---

## 4. Mock / dev environment services

**Local "mini cloud":**

- **Docker Compose** — Define several services (app, DB, queue, cache) in one YAML; one command brings up a small distributed env.
- **Kubernetes (minikube, kind, k3d)** — Real K8s locally for testing manifests, operators, scheduling.
- **Tilt / Skaffold** — Watch code and rebuild/redeploy into a local K8s cluster.

**Mock / simulated services:**

- **LocalStack** — Mocks many AWS APIs (S3, SQS, Lambda, etc.) locally.
- **WireMock / MockServer** — HTTP APIs that return predefined or dynamic responses.
- **Testcontainers** — Start real DBs, message brokers, etc., in containers from test code.
- **Pact** — Contract testing; consumer defines contract; provider tests against it.

**Cloud dev environments:**

- **Ephemeral / preview environments** — Per branch or PR (e.g. Vercel preview, Heroku review apps).
- **AWS / GCP / Azure** — Separate dev account or project; use IaC so "dev" is repeatable.

---

## 5. AWS services (what they do)

Grouped by area. Names and roles only; details are in AWS docs.

### Compute

| Service | What it does |
|---------|----------------|
| **EC2** | Virtual servers (VMs). You manage OS and app; AWS manages hardware and hypervisor. |
| **Lambda** | Run code in response to events or HTTP, without managing servers. Pay per invocation and duration. |
| **ECS (Elastic Container Service)** | Run Docker containers. Task = unit of work; Service = keeps N tasks running. |
| **EKS (Elastic Kubernetes Service)** | Managed Kubernetes. AWS runs control plane; you run worker nodes (or Fargate). |
| **Fargate** | Serverless compute for containers. Run ECS tasks or EKS pods without managing EC2. |
| **App Runner** | Fully managed service to run web apps and APIs from source or container. Simple deploy, auto-scaling. |
| **Batch** | Run batch jobs (e.g. nightly jobs, HPC) at scale. Schedules onto EC2 or Fargate. |
| **Lightsail** | Simplified VPS + optional LB, DNS, storage. Good for small apps and learning. |

### Storage

| Service | What it does |
|---------|----------------|
| **S3** | Object storage (files, blobs). Buckets and keys; versioning, lifecycle, events. |
| **EBS** | Block storage attached to EC2 (disks). Persistent; snapshots for backup/copy. |
| **EFS** | Managed NFS. Shared file system across EC2 (and Lambda with mount). |
| **FSx** | Managed file systems (Windows FSx, Lustre for HPC, NetApp ONTAP, OpenZFS). |
| **S3 Glacier** | Archive storage. Cheaper, retrieval delay; for long-term backup/compliance. |

### Database & data

| Service | What it does |
|---------|----------------|
| **RDS** | Managed relational DB (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server). Multi-AZ, read replicas. |
| **Aurora** | MySQL/PostgreSQL-compatible, high availability, auto-scaling storage, global DB. |
| **DynamoDB** | Managed NoSQL key-value/document. Serverless; single-digit ms latency at scale. |
| **ElastiCache** | Managed Redis or Memcached. In-memory cache or session store. |
| **DocumentDB** | MongoDB-compatible managed document DB. |
| **Keyspaces** | Managed Apache Cassandra–compatible wide-column DB. |
| **Redshift** | Data warehouse. SQL analytics on large datasets. |
| **OpenSearch** | Managed Elasticsearch/OpenSearch. Search, log analytics, dashboards. |

### Networking & content delivery

| Service | What it does |
|---------|----------------|
| **VPC** | Isolated network (CIDR, subnets, route tables). Foundation for EC2, RDS, Lambda (in VPC), etc. |
| **CloudFront** | CDN. Cache and serve content at edge; DDoS mitigation (Shield); optional custom origins. |
| **Route 53** | DNS and health checks. Routing policies (latency, failover, weighted). |
| **API Gateway** | REST/WebSocket APIs in front of Lambda, HTTP backends, or other AWS services. Auth, throttling, keys. |
| **Direct Connect** | Dedicated physical link from your DC to AWS. Private, predictable network. |
| **Global Accelerator** | Improve global availability and performance via AWS edge; static IPs, health-based routing. |
| **PrivateLink** | Expose a service in your VPC to other VPCs or on-prem without public internet. |

### Load balancing (see also Section 6)

| Service | What it does |
|---------|----------------|
| **ALB (Application Load Balancer)** | L7 HTTP/HTTPS. Path- and host-based routing; WebSockets; target groups (EC2, IP, Lambda). |
| **NLB (Network Load Balancer)** | L4 TCP/UDP. Low latency, static IP, preservation of client IP; for non-HTTP or extreme performance. |
| **Gateway Load Balancer** | Deploy and scale third-party virtual appliances (firewalls, IDS) in the traffic path. |

### Messaging & streaming

| Service | What it does |
|---------|----------------|
| **SQS** | Message queue. Decouple producers and consumers; at-least-once delivery; standard vs FIFO. |
| **SNS** | Pub/sub. Fan-out to many subscribers (SQS, Lambda, HTTP, email, etc.). |
| **EventBridge** | Event bus. Route events by rule (schedule, AWS services, custom); event-driven and scheduled workflows. |
| **Kinesis Data Streams** | Ordered, durable streams. Real-time ingest and process (e.g. clickstream, logs). |
| **Kinesis Data Firehose** | Load streaming data into S3, Redshift, OpenSearch, etc. with minimal code. |
| **MQ** | Managed ActiveMQ. Traditional message broker (JMS, AMQP) when you need broker semantics. |

### Security & identity

| Service | What it does |
|---------|----------------|
| **IAM** | Users, roles, policies. Who can do what on which resource (principle of least privilege). |
| **Cognito** | User pools (sign-up/sign-in) and identity pools (temp AWS creds for guests). |
| **Secrets Manager** | Store and rotate secrets (DB credentials, API keys); retrieve from app at runtime. |
| **Parameter Store (SSM)** | Key-value config and secrets; hierarchy; integration with Lambda, ECS, etc. |
| **WAF** | Web application firewall. Rules on CloudFront/ALB (IP, geo, rate, managed rule groups). |
| **Shield** | DDoS protection (Standard always on; Advanced for higher support and cost). |
| **GuardDuty** | Threat detection from VPC flow logs, DNS, CloudTrail, etc. |
| **KMS** | Create and manage keys for encryption (EBS, S3, etc.) and signing. |

### Observability & operations

| Service | What it does |
|---------|----------------|
| **CloudWatch** | Metrics, logs, alarms, dashboards. Default destination for many AWS resources. |
| **CloudWatch Logs** | Ingest, query (Logs Insights), and retain log streams. |
| **X-Ray** | Distributed tracing. Map requests across services and find bottlenecks. |
| **CloudTrail** | Audit log of API calls (who did what, when). |
| **Config** | Record and evaluate configuration changes and compliance rules. |
| **Systems Manager (SSM)** | Run commands, patch, manage parameters, Session Manager (SSH-less access) on EC2. |

### Containers & deployment

| Service | What it does |
|---------|----------------|
| **ECR** | Docker image registry. Push/pull from ECS, EKS, Lambda, or local. |
| **CodePipeline** | Orchestrate build, test, deploy (CodeBuild, CodeDeploy, third-party). |
| **CodeBuild** | Run build jobs (compile, test, package) in managed environments. |
| **CodeDeploy** | Deploy to EC2, Lambda, or ECS (rolling, blue/green, canary). |
| **CodeStar** | Project templates and pipelines (GitHub/GitLab, CodeBuild, CodeDeploy). |

---

## 6. Orchestrators, load balancers, and related concepts

### Orchestration (scheduling and placement)

| Term / system | Meaning |
|---------------|--------|
| **Orchestrator** | System that decides *where* and *when* to run workloads (which node, how many replicas, restarts). |
| **Kubernetes (K8s)** | Orchestrator for containers. Pods, Deployments, Services, Ingress; declarative YAML; ecosystem (Helm, operators). |
| **ECS** | AWS container orchestrator. Task definitions (CPU/memory, image); Services keep tasks running; optional Fargate. |
| **EKS** | Managed Kubernetes on AWS. Same K8s API; AWS runs control plane; you or Fargate run nodes. |
| **Swarm** | Docker’s built-in orchestrator (simpler than K8s; less common in production). |
| **Nomad** | HashiCorp orchestrator for containers and non-container workloads; multi-region, flexible. |
| **Scheduler** | Component that assigns work to nodes (e.g. K8s scheduler, ECS placement). |
| **Reconciliation loop** | Controller repeatedly compares desired state (YAML) to actual state and fixes drift (e.g. "ensure 3 replicas"). |
| **Operator** | Controller that extends K8s to manage custom resources (e.g. DB, message broker) via CRDs. |

### Load balancing

| Term / component | Meaning |
|------------------|--------|
| **Load balancer (LB)** | Distributes traffic across multiple targets (instances, containers, IPs) for availability and scaling. |
| **L4 (Layer 4)** | TCP/UDP. No awareness of HTTP; fast, low latency. Example: NLB. |
| **L7 (Layer 7)** | HTTP/HTTPS. Path, host, headers; sticky sessions; TLS termination. Example: ALB. |
| **ALB** | Application Load Balancer. L7; path- and host-based routing; target groups; health checks. |
| **NLB** | Network Load Balancer. L4; static IPs; used for non-HTTP or when you need minimal latency. |
| **Target group** | Set of targets (e.g. EC2, IP, Lambda) behind an ALB/NLB. Health checks and routing rules reference them. |
| **Health check** | LB or orchestrator periodically probes a target (HTTP, TCP). Unhealthy targets get no traffic. |
| **Sticky session (session affinity)** | Same client sent to same target (e.g. cookie-based on ALB). |
| **Round robin** | Rotate traffic evenly across targets. |
| **Least connections** | Send traffic to the target with fewest active connections (when supported). |
| **Ingress** | In K8s, object that defines HTTP(S) routes into the cluster; often implemented by an Ingress controller (e.g. ALB Ingress Controller). |
| **Service (K8s)** | Stable endpoint (DNS and/or ClusterIP/LoadBalancer/NodePort) for a set of pods; often fronted by an LB in cloud. |

### High availability (HA) and scaling

| Term | Meaning |
|------|--------|
| **High availability (HA)** | Design so single failures (AZ, node, process) don’t take down the app. Multi-AZ, multiple replicas. |
| **Availability Zone (AZ)** | Isolated datacenter within a region. Multi-AZ = spread across AZs for failure isolation. |
| **Auto Scaling** | Add/remove EC2 instances (or similar) based on metrics or schedule. ASG = Auto Scaling Group. |
| **Horizontal scaling** | Add more instances/pods (scale out). Contrast: vertical = bigger instance (scale up). |
| **Desired capacity** | In ASG or ECS/K8s: how many instances or tasks/pods you want running. |
| **Min / max size** | ASG bounds; orchestrator keeps count between these. |
| **Blue/green** | Two identical environments; switch traffic from "blue" to "green" after deploy. Fast rollback by switching back. |
| **Canary** | Send a small % of traffic to new version; increase if metrics are good. |
| **Rolling update** | Replace instances/pods gradually (e.g. one at a time) to avoid downtime. |

### Related concepts

| Term | Meaning |
|------|--------|
| **Service discovery** | How processes find each other (DNS names, registry). In K8s: Services and DNS; in ECS: service discovery namespace. |
| **Circuit breaker** | Stop calling a failing dependency after repeated failures; fail fast and optionally retry later. |
| **Bulkhead** | Isolate resources (e.g. thread pool, connection pool) so one failing component doesn’t starve others. |
| **Rate limiting** | Cap requests per client or per API to protect backends. Often at API Gateway or WAF. |
| **Backpressure** | When a consumer is slow, signal producers to slow down (e.g. in streams/queues). |
| **Graceful shutdown** | Process stops accepting new work, finishes in-flight, then exits. LBs stop sending traffic when health check fails. |
| **Probe (K8s)** | Liveness = is the process alive? Restart if not. Readiness = should we send traffic? Remove from LB if not. |

---

## Quick links (by focus)

- **DevOps flow** → Section 1  
- **Scripting** → Section 2  
- **Distributed testing** → Section 3  
- **Local/mock envs** → Section 4  
- **AWS services** → Section 5  
- **Orchestration & load balancing** → Section 6  

---

*Part of the [[index]] compendium. See also [[Open-Source-Tools]] for tooling lore.*
