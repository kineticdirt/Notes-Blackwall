# Assistant on Kubernetes

Run the general-purpose assistant in a pod with Claude (Anthropic), internet access, and HTTP API.

## 1. Put your API key in a file (local)

Create the key file (do not commit it):

```bash
echo "sk-ant-api03-YOUR-KEY" > assistant/llm_keys/ANTHROPIC_API_KEY
```

See `assistant/llm_keys/README.md` for details.

## 2. Build image

From the **repo root**:

```bash
docker build -f assistant/Dockerfile -t assistant:latest .
```

## 3. Create Kubernetes secret from key file

```bash
kubectl create secret generic assistant-llm-key \
  --from-file=ANTHROPIC_API_KEY=assistant/llm_keys/ANTHROPIC_API_KEY
```

Or with literal (avoid leaving key on disk):

```bash
kubectl create secret generic assistant-llm-key \
  --from-literal=ANTHROPIC_API_KEY='sk-ant-api03-...'
```

## 4. Deploy

```bash
kubectl apply -f assistant/k8s/configmap.yaml
kubectl apply -f assistant/k8s/secret.yaml   # or create secret first (step 3)
kubectl apply -f assistant/k8s/deployment.yaml
kubectl apply -f assistant/k8s/service.yaml
```

## 5. Test

- **From inside the cluster:** `curl -X POST http://assistant.default.svc.cluster.local:8765/message -H "Content-Type: application/json" -d '{"message":"Hello, can you access the internet?"}'`
- **Port-forward and test locally:**
  ```bash
  kubectl port-forward deployment/assistant 8765:8765
  curl -X POST http://localhost:8765/message -H "Content-Type: application/json" -d '{"message":"Hello"}'
  ```

The pod has normal egress (internet) by default, so the assistant can call the Anthropic API and any tools that need network access.

## Capabilities to test

- **Internet / external APIs:** Claude runs in the cloud; the pod only needs outbound HTTPS to `api.anthropic.com`.
- **Relevant information:** Use the assistant’s tools (read_file, grep, codebase_search, etc.) and preferences; optional MCP servers can be configured via `PI_MCP_CONFIG` if you add them to the image or mount a config.

## Optional: LoadBalancer or Ingress

To expose the service outside the cluster, change the Service to `type: LoadBalancer` or add an Ingress pointing to `assistant:8765`.
