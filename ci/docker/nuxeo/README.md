# Nuxeo Docker image for MCP demo server

Build the image:

```bash
docker buildx build --platform linux/amd64 --build-arg CLID=${CLID} --tag docker-internal.packages.nuxeo.com/nuxeo/nuxeo-mcp-demo:2025 .
```

The image integrates a nuxeo.conf file that retrieve the environment variable `NUXEO_JWT_SECRET` to configure 
`nuxeo.jwt.secret`.
