
The default Docker image used in the unit tests (`nuxeo/nuxeo:latest`) is small and starts quickly, however it also has some limitations:

 - when running on ARM the native ARM image is missing a lot of converters
    - all conversions capabilities are disabled
 - the OpenSearch package is not installed so fulltext search and complex queries are not available

For Demo and experimentation purposes, it is better to use the image `nuxeo/nuxeo-mcp-demo:2025`

    docker run -ti -p 8080:8080 docker-internal.packages.nuxeo.com/nuxeo/nuxeo-mcp-demo:2025

This image:

 - is x86 only so openoffice and all converters are present
 - contains opensearch
 - contains showcase content
 - contains a UI

As as side effect, the image is much bigger and takes much more time to start especially on ARM platform (80s vs 4s !) 



