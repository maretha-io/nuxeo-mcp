
I want to use pytest `marker` to define different tests profiles.

Add the markers definition in pyproject.toml

I want to define an `integration` marker that will allow to run `test_server` without having to mock the nuxeoclient nor the MCP Server.
Typically, this will include the tests/test_serverpy::test_nuxeo_client_connection that is currently skipped.

For the integration tests :

 - start the Nuxeo server via Docker
 - check that Nuxeo is running using the health_check http://localhost:8080/nuxeo/runningstatus

I also want to debug this jwt error in the Nuxeo client.


