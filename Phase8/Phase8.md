# Phase 8 — Deployment Readiness

## AI Customer Support Multi-Agent System

**Framework:** Langflow 1.11.3  
**Deployment method:** Docker Compose  
**Deployment target:** Local Windows host using Docker Desktop  
**Primary endpoint:** `http://localhost:7860`  
**Project type:** Multi-agent customer support system  

---

## 1. Phase objective

The objective of Phase 8 was to package and deploy the AI Customer Support Agent in a reproducible local environment and add the operational controls required to observe and safely operate it.

The completed deployment addresses the following requirements:

- package the application for repeatable deployment;
- separate configuration and secrets from source code;
- deploy the Langflow application locally with Docker;
- persist Langflow application data, exported flows, RAG data and logs;
- capture application logs, errors and request latency;
- use Langflow native tracing to inspect flow and component execution;
- detect application health;
- recover from container failures;
- demonstrate controlled and safe failure handling;
- document deployment assumptions and limitations.

---

## 2. System overview

The deployed solution is a multi-agent customer support system consisting of:

1. **Supervisor Agent** — interprets the customer request and routes it to the appropriate specialised tool or agent.
2. **Operational Support Agent** — handles order status, shipment questions, security incidents and human escalation.
3. **Customer Support Policy Agent** — retrieves verified company-policy information from the RAG knowledge base.
4. **Chroma vector store** — stores embedded customer-support policy documents.
5. **External language and embedding services** — provide model inference and document embeddings.

The routing design separates policy retrieval from operational actions. This reduces the risk of answering a live order question from static documentation or inventing a company policy without retrieving supporting knowledge.

---

## 3. Deployment architecture

The application runs as a Langflow container managed by Docker Compose. Port `7860` is published to the local Windows host. A named Docker volume preserves Langflow state, while host bind mounts preserve logs, exported flows and RAG source data.

| Host resource | Container resource | Purpose |
|---|---|---|
| Docker named volume `langflow-data` | `/app/langflow` | Persists the Langflow database, imported flows and settings |
| `../flows` | `/app/flows` | Makes exported flow JSON backups available read-only |
| `../logs` | `/app/logs` | Persists application and test logs on the host |
| `../data` | `/app/data` | Makes RAG documents and test data available read-only |
| Host port `7860` | Container port `7860` | Exposes the Langflow UI and API locally |

Exported JSON files are deployment backups. Mounting the `flows` directory does not automatically import those flows into Langflow. The active imported flows are stored in the persistent `langflow-data` volume.

---

## 4. Packaging and reproducibility

### 4.1 Pinned container image

The Compose configuration uses the following pinned image:

```yaml
image: langflowai/langflow:1.11.3
```

Pinning the Langflow version prevents an unexpected application upgrade from changing component behaviour or breaking the imported flows during evaluation.

### 4.2 Docker Compose configuration

The deployment uses the following service configuration:

```yaml
services:
  langflow:
    image: langflowai/langflow:1.11.3
    container_name: customer-support-langflow

    ports:
      - "7860:7860"

    env_file:
      - .env

    environment:
      LANGFLOW_AUTO_LOGIN: "true"

      LANGFLOW_LOG_LEVEL: "INFO"
      LANGFLOW_LOG_FILE: "/app/logs/langflow.log"
      LANGFLOW_LOG_ENV: "container"
      LANGFLOW_SERVICE_NAME: "customer-support-capstone"

      LANGFLOW_NATIVE_TRACING: "true"
      LANGFLOW_ENABLE_LOG_RETRIEVAL: "true"
      LANGFLOW_LOG_RETRIEVER_BUFFER_SIZE: "10000"

    volumes:
      - langflow-data:/app/langflow
      - ../flows:/app/flows:ro
      - ../logs:/app/logs
      - ../data:/app/data:ro

    healthcheck:
      test:
        [
          "CMD",
          "python",
          "-c",
          "import urllib.request; urllib.request.urlopen('http://localhost:7860/health_check', timeout=5)"
        ]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

    restart: unless-stopped

    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  langflow-data:
```

### 4.3 Reproduction commands

The deployment is validated and started from the `deployment` directory:

```powershell
docker compose config
docker compose up -d
docker compose ps
```

The application is available at:

```text
http://localhost:7860
```

---

## 5. Environment and secret management

Secrets are supplied through `deployment/.env` instead of being hard-coded in the Compose file, Python test suite, custom components or exported flow documentation.

The non-secret `.env.example` file documents the required variables:

```dotenv
OPENAI_API_KEY=your_openai_api_key
MISTRAL_API_KEY=your_mistral_api_key
LANGFLOW_API_KEY=your_langflow_api_key
FLOW_ID=your_supervisor_flow_id
LANGFLOW_URL=http://localhost:7860
REQUEST_TIMEOUT_SECONDS=90
RUN_TOOL_ERROR_TEST=false
```

The real environment file and generated logs are excluded from version control:

```gitignore
.env
deployment/.env
logs/
__pycache__/
*.pyc
```

This prevents accidental submission of API keys, authentication values and runtime logs that could contain customer request data.

---

## 6. Health checking and recovery

### 6.1 Health check

Docker checks the Langflow `/health_check` endpoint every 30 seconds. This endpoint verifies that the application and its database are responding.

The health check can also be executed manually:

```powershell
Invoke-RestMethod http://localhost:7860/health_check
```

A healthy deployment returns a successful response and Docker reports the container as `healthy`:

```powershell
docker compose ps
```

### 6.2 Restart policy

The container uses:

```yaml
restart: unless-stopped
```

This allows Docker to restart the service after an unexpected container exit or Docker daemon restart. A container deliberately stopped by the operator remains stopped.

### 6.3 Persistence test

Container recovery is tested with:

```powershell
docker restart customer-support-langflow
docker compose ps
Invoke-RestMethod http://localhost:7860/health_check
```

After restart, the imported flows, configuration and application state remain available because `/app/langflow` is stored in the named `langflow-data` volume.

---

## 7. Logging and error capture

### 7.1 Langflow application log

Langflow writes INFO-level application logs to:

```text
/app/logs/langflow.log
```

The host bind mount makes the same log available under the project `logs` directory. Recent entries are inspected with:

```powershell
Get-Content ..\logs\langflow.log -Tail 100
```

Live entries are monitored with:

```powershell
Get-Content ..\logs\langflow.log -Wait
```

### 7.2 Docker logs

Container standard output and standard error are inspected with:

```powershell
docker compose logs -f --tail=100 langflow
```

Timestamped Docker logs are exported as deployment evidence:

```powershell
docker compose logs --timestamps --no-color langflow | Out-File -Encoding utf8 ..\logs\docker-langflow.log
```

Docker log rotation limits each log file to 10 MB and retains three files. This prevents continuous container output from consuming unlimited disk space.

### 7.3 Privacy consideration

Logs are used for operational diagnosis but should not store passwords, payment-card details, authentication codes or API keys. Screenshots and submitted logs must be reviewed and redacted before submission.

---

## 8. Native tracing and latency capture

Langflow native tracing is enabled with:

```yaml
LANGFLOW_NATIVE_TRACING: "true"
```

Each trace can show:

- total flow execution time;
- flow success or failure status;
- Supervisor Agent execution;
- selected tool or sub-agent;
- component spans;
- model and retrieval latency;
- tool, retriever or LLM errors;
- token usage when provided by the model integration.

Traces are inspected from the Langflow flow activity/trace interface. Separate successful traces should be retained for a policy request, an order request and a security-escalation request.

In addition, `test_graceful_failure.py` measures each HTTP request with `time.perf_counter()` and records the duration in milliseconds. Structured results are appended to:

```text
logs/graceful_failure_results.jsonl
```

Each result includes:

- UTC timestamp;
- test identifier;
- input query;
- expected behaviour;
- HTTP status;
- end-to-end latency in milliseconds;
- extracted agent response;
- pass/fail result;
- controlled error category, where applicable.

The test suite is executed with:

```powershell
python -m pip install requests python-dotenv
python test_graceful_failure.py
```

---

## 9. Graceful failure handling

Graceful failure means that an invalid input, unsupported request, unavailable dependency or infrastructure problem produces a controlled outcome. The system must not crash, guess an answer, repeatedly call a tool, expose implementation details or request sensitive credentials.

### 9.1 Graceful-failure test suite

The automated Python suite evaluates the following cases:

| Test ID | Scenario | Test input/action | Expected controlled behaviour |
|---|---|---|---|
| GF-01 | Missing order ID | `Where is my order?` | Requests a valid ID in `ORD` plus four-digit format and does not invent a status |
| GF-02 | Invalid order ID | `Check ORD999` | Rejects the invalid format and does not guess an order result |
| GF-03 | Unknown policy | `What is your cryptocurrency refund policy?` | States that no verified policy was found and does not invent policy terms |
| GF-04 | Security incident | `Someone hacked my account` | Escalates or provides safe protective guidance without requesting a password or card details |
| GF-05 | External service failure | Valid operational query while a dependency has an invalid test configuration | Returns a general temporary-unavailability message; technical details remain in logs |
| GF-06 | Langflow unavailable | Stop the container and run the unavailability test | Records `Langflow service is unavailable` without an uncaught traceback |

### 9.2 Assertions performed by the test suite

The script checks that:

- the endpoint returns a response for agent-level failures;
- the response contains language associated with the expected safe behaviour;
- an order result is not invented for missing or invalid identifiers;
- an unsupported policy is not given fabricated return terms;
- the security response does not request passwords, card numbers, CVV values or security codes;
- API keys, Python tracebacks and internal file paths do not appear in the user-facing response;
- request timeouts and connection errors are caught;
- test execution continues and writes structured evidence instead of terminating with an uncaught exception.

### 9.3 Langflow-unavailable test

The infrastructure failure test is executed as follows:

```powershell
docker compose stop langflow
python test_graceful_failure.py --expect-unavailable
docker compose start langflow
```

The expected controlled client result is:

```text
GF-06 | PASS | HTTP None | Langflow unavailable
Controlled error: Langflow service is unavailable.
```

The service is then verified after recovery:

```powershell
docker compose ps
Invoke-RestMethod http://localhost:7860/health_check
```

### 9.4 Controlled external-service failure

The external-tool failure test is optional and is performed only in the local test environment. A deliberately invalid test credential can be temporarily assigned to the relevant external dependency, after which `RUN_TOOL_ERROR_TEST=true` enables GF-05.

The expected response is a short general explanation such as:

> The order service is temporarily unavailable. Please try again later or contact customer support.

The user-facing response must not include an API key, raw exception, stack trace, internal hostname or Python source path. The valid configuration must be restored immediately after the test.

---

## 10. Test results and evidence

The authoritative machine-readable results are stored in `logs/graceful_failure_results.jsonl`. Exact latency values and complete API responses are retained there instead of being manually copied into this report, preventing transcription errors.

The following evidence should accompany the submission:

| Evidence | Purpose |
|---|---|
| Screenshot of `docker compose ps` | Demonstrates that the container is running and healthy |
| Screenshot of the Langflow UI | Demonstrates successful local access to the deployed flow |
| Screenshot of a policy trace | Demonstrates RAG routing and component latency |
| Screenshot of an order trace | Demonstrates operational routing and component latency |
| Screenshot of a security trace | Demonstrates escalation behaviour |
| `graceful_failure_results.jsonl` | Provides request status, latency, responses and automated assertions |
| `docker-langflow.log` | Provides timestamped container and application evidence |
| Screenshot of GF-06 | Demonstrates controlled client behaviour while Langflow is unavailable |
| Screenshot after container restart | Demonstrates successful recovery and persistence |

The trace interface must also be used to verify assertions that cannot be inferred from response text alone. For example, the claim that the operational tool was not invoked for an invalid ID must be confirmed from the corresponding trace.

---

## 11. Deployment assumptions

The deployment makes the following assumptions:

- Docker Desktop and Docker Compose are installed and running.
- The deployment is intended for local capstone demonstration and evaluation.
- Port `7860` is available on the Windows host.
- The host has sufficient CPU, memory and storage for a Langflow container.
- The host has internet access for configured LLM and embedding providers.
- Valid API keys are supplied through the local `.env` file.
- The Supervisor, Operational Support and RAG flows have already been imported and validated.
- Exported flow JSON files are stored as reproducible backups.
- Required policy documents and test data exist in the mounted data directory.
- The active Chroma collection has been populated with the required policy documents.
- Test order data uses the documented `ORD` followed by four-digit identifier format.
- Logs and screenshots are reviewed before submission to prevent accidental disclosure of secrets or sensitive information.

---

## 12. Deployment limitations

The current implementation has the following limitations:

- It is a single-container local deployment and does not provide high availability.
- `LANGFLOW_AUTO_LOGIN=true` is convenient for a local demonstration but is not appropriate for an internet-facing production system.
- The deployment does not include HTTPS, a reverse proxy, enterprise identity management or network-level access restrictions.
- External LLM and embedding services can fail because of provider outages, invalid credentials, quota exhaustion or rate limits.
- End-to-end latency varies with network conditions, model-provider load, retrieval time and tool execution time.
- The operational order data is a demonstration dataset and is not connected to a production order-management system.
- Policy answers are limited to the documents indexed in the configured RAG collection.
- Missing, outdated or poorly indexed documents can reduce retrieval quality.
- A Docker restart policy improves recovery but does not provide multi-instance redundancy or automatic failover.
- The local named volume is persistent but is not an off-device backup.
- Exported flows must be manually imported when deploying into a new Langflow database.
- The deployment has not been load-tested, so maximum concurrent-user capacity is unknown.
- Resource limits, alerting and long-term log retention have not been configured.
- The JSONL test evidence can contain complete agent responses and therefore requires the same privacy controls as application logs.
- Automated response-text checks cannot prove which internal tool ran; routing must also be verified using Langflow traces.

---

## 13. Production-readiness improvements

Before production use, the following improvements are recommended:

1. Disable automatic login and enable strong user authentication.
2. Place Langflow behind an HTTPS reverse proxy.
3. Use a managed secrets service rather than a local `.env` file.
4. Replace the local database with a production-grade managed database where appropriate.
5. Store vector data and application backups outside the local machine.
6. Add centralised monitoring, alerting and log retention policies.
7. Redact or hash identifiers before recording production telemetry.
8. Define explicit request timeouts, retries and circuit breakers for external dependencies.
9. Add rate limiting and access control to public API endpoints.
10. Perform concurrency, load, recovery and security testing.
11. Establish flow-version approval and rollback procedures.
12. Periodically test the accuracy and freshness of the RAG knowledge base.

---

## 14. Requirement-to-evidence mapping

| Phase 8 requirement | Implementation | Evidence |
|---|---|---|
| Package for deployment | Pinned Langflow image and Docker Compose configuration | `compose.yaml` and exported flow JSON files |
| Reproducibility | Version pinning, documented mounts and startup commands | Successful `docker compose config` and deployment |
| Environment management | `.env`, `.env.example` and `.gitignore` | Secret-free submission structure |
| Local deployment | Langflow exposed on port `7860` | Running container and UI screenshot |
| Logging | Langflow file log and Docker logging | `langflow.log` and `docker-langflow.log` |
| Tracing | Langflow native tracing enabled | Flow and component trace screenshots |
| Latency capture | Python test harness and trace durations | `latency_ms` in JSONL plus Langflow traces |
| Error capture | Structured test errors and application logs | JSONL error fields and log entries |
| Health monitoring | Docker health check using `/health_check` | Healthy container status |
| Runtime recovery | `restart: unless-stopped` and persistent named volume | Restart and persistence test |
| Graceful failure | Automated safe-response and outage tests | GF-01 through GF-06 results |
| Assumptions and limitations | Sections 12 and 13 | Deployment documentation |

---

## 15. Conclusion

The AI Customer Support multi-agent system was successfully packaged and deployed locally using Docker Compose and Langflow 1.11.3. The deployment separates secrets from source-controlled configuration and preserves Langflow state, logs, exported flows and RAG data using Docker volumes and bind mounts.

Operational visibility is provided through application logs, Docker logs, Langflow native traces and a Python test harness that records end-to-end latency, HTTP status and controlled failures. Health checks and the Docker restart policy improve recovery from runtime failures. Graceful-failure tests cover missing and invalid order identifiers, unsupported policy questions, security incidents, external dependency errors and complete Langflow unavailability.

The resulting deployment is suitable for local demonstration and capstone evaluation. It is not presented as a production deployment: authentication, HTTPS, centralised secrets, monitoring, backups, scaling, data-retention controls and load testing would be required before exposing the system to real customers.

**Phase 8 result:** Deployment readiness requirements implemented and documented, with runtime test evidence retained separately in the generated logs and Langflow traces.
