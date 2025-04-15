# Project: Simple Daily Data Fetcher

## Goal

Create an automated pipeline that fetches data from a public API daily, performs a simple transformation, runs tests, builds a Docker image, provisions a placeholder resource using Terraform, and runs the container.

## Review

1. We have created:
    - A Python script fetching and processing data.
    - Unit tests and linting for code quality.
    - A Dockerfile to containerize the script.
    - A GitHub Actions workflow automating:
        - Testing & Linting (CI)
        - Docker Image Building & Pushing (CI artifact)
        - Basic Infrastructure Provisioning via Terraform (IaC demo)
        - Running the container job (CD - simple execution)

2. **Concepts Covered**: Git, Python, Testing, Docker, GitHub Actions (CI/CD, Secrets GITHUB_TOKEN), Terraform (IaC basics), basic logging.

3. **Security**: Using GITHUB_TOKEN for secure auth to ghcr.io. For real cloud credentials (AWS/GCP/Azure) in Terraform, you'd store them as encrypted secrets in GitHub repository settings (Settings > Secrets and variables > Actions).

4. **Monitoring**: Integrate Prometheus/Grafana (runnable locally via Docker Compose) to scrape basic metrics.

5. **Parameterization**: Use environment variables or command-line arguments in the Python script (and Dockerfile) to make things like the output filename or API category configurable.

## TODO

- [] Kubernetes deployment
- [] real cloud infrastructure (AWS/GCP)