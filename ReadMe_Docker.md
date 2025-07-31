
# Multi-Arch Docker Build and Push to AWS ECR (via AWS SSO)

This guide walks you through:

 - building a multi-architecture Docker image  (`linux/amd64` on Mac ARM) 
 - pushing it to an AWS ECR using AWS SSO

## 1. Activate Multi-Architecture Build Support

Create and bootstrap a `buildx` builder that supports multi-architecture builds:

```bash
docker buildx create --name multiarch-builder --use
docker buildx inspect --bootstrap
````

Verify that the builder is available and ready:

```bash
docker buildx ls
```

## 2. Run a Test Build (Sanity Check)

Build a native `arm64` image to verify that your Dockerfile and context are correct:

```bash
docker buildx build \
  --platform linux/arm64 \
  --load \
  -t nuxeo-mcp-arm64:latest \
  .
```

> `--load` allows you to load the image into your local Docker engine for testing.

## 3. Authenticate to AWS SSO

Login using your AWS SSO profile:

```bash
aws sso login --profile hxai-sandbox
```

## 4. Authenticate Docker with ECR

Retrieve a login token for ECR and pass it to Docker:

```bash
aws ecr get-login-password --region us-east-1 --profile hxai-sandbox \
  | docker login --username AWS --password-stdin 407995386968.dkr.ecr.us-east-1.amazonaws.com
```

## 5. Build and Push the `linux/amd64` Image

Now build the image for `linux/amd64` and push it directly to your AWS ECR repository:

```bash
docker buildx build \
  --platform linux/amd64 \
  -t 407995386968.dkr.ecr.us-east-1.amazonaws.com/cin-agentbuilder-mcp-sandbox-nuxeo-mcp:latest \
  --push \
  .
```

Once complete, the image will be available in ECR at:

```
407995386968.dkr.ecr.us-east-1.amazonaws.com/cin-agentbuilder-mcp-sandbox-nuxeo-mcp:latest
```
