"""
Unit tests for authentication components.
"""

import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, PropertyMock
import pytest

from nuxeo_mcp.config import (
    AuthMethod,
    OAuth2Config,
    NuxeoServerConfig,
    MCPAuthConfig,
)
from nuxeo_mcp.token_store import OAuth2Token, EncryptedFileStorage, TokenManager
from nuxeo_mcp.auth import BasicAuthHandler, OAuth2AuthHandler
from nuxeo_mcp.middleware import AuthMiddleware, AuthenticationManager


class TestOAuth2Config:
    """Test OAuth2 configuration."""
    
    def test_oauth2_config_from_env(self):
        """Test creating OAuth2Config from environment variables."""
        with patch.dict(os.environ, {
            'NUXEO_OAUTH_CLIENT_ID': 'test-client-id',
            'NUXEO_OAUTH_CLIENT_SECRET': 'test-secret',
            'NUXEO_OAUTH_REDIRECT_PORT': '8888',
            'NUXEO_OAUTH_SCOPE': 'custom scope',
        }):
            config = OAuth2Config.from_env()
            assert config is not None
            assert config.client_id == 'test-client-id'
            assert config.client_secret == 'test-secret'
            assert config.redirect_port == 8888
            assert config.scope == 'custom scope'
    
    def test_oauth2_config_from_env_missing(self):
        """Test OAuth2Config returns None when required env vars missing."""
        with patch.dict(os.environ, {}, clear=True):
            config = OAuth2Config.from_env()
            assert config is None


class TestNuxeoServerConfig:
    """Test Nuxeo server configuration."""
    
    def test_basic_auth_config(self):
        """Test basic authentication configuration."""
        config = NuxeoServerConfig(
            url="http://localhost:8080/nuxeo",
            auth_method=AuthMethod.BASIC,
            username="admin",
            password="password",
        )
        assert config.auth_method == AuthMethod.BASIC
        assert config.username == "admin"
        assert config.password == "password"
    
    def test_oauth2_config(self):
        """Test OAuth2 configuration."""
        oauth2 = OAuth2Config(
            client_id="test-client",
            client_secret="test-secret",
        )
        config = NuxeoServerConfig(
            url="http://localhost:8080/nuxeo",
            auth_method=AuthMethod.OAUTH2,
            oauth2_config=oauth2,
        )
        assert config.auth_method == AuthMethod.OAUTH2
        assert config.oauth2_config.client_id == "test-client"
    
    def test_invalid_basic_auth_config(self):
        """Test that basic auth requires username and password."""
        with pytest.raises(ValueError, match="Username and password required"):
            NuxeoServerConfig(
                url="http://localhost:8080/nuxeo",
                auth_method=AuthMethod.BASIC,
            )
    
    def test_invalid_oauth2_config(self):
        """Test that OAuth2 requires oauth2_config."""
        with pytest.raises(ValueError, match="OAuth2 configuration required"):
            NuxeoServerConfig(
                url="http://localhost:8080/nuxeo",
                auth_method=AuthMethod.OAUTH2,
            )


class TestMCPAuthConfig:
    """Test MCP authentication configuration."""
    
    def test_default_config_path(self):
        """Test default configuration path generation."""
        config = MCPAuthConfig()
        assert config.config_file_path is not None
        assert "nuxeo-mcp" in str(config.config_file_path)
    
    def test_add_server(self):
        """Test adding server configurations."""
        config = MCPAuthConfig()
        server_config = NuxeoServerConfig(
            url="http://test.nuxeo.com",
            auth_method=AuthMethod.BASIC,
            username="user",
            password="pass",
        )
        config.add_server("test", server_config)
        
        assert "test" in config.servers
        assert config.default_server == "test"
        assert config.get_server_config("test") == server_config
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            
            # Create and save config
            config = MCPAuthConfig(config_file_path=config_path)
            oauth2 = OAuth2Config(
                client_id="test-client",
                client_secret="test-secret",
            )
            server_config = NuxeoServerConfig(
                url="http://test.nuxeo.com",
                auth_method=AuthMethod.OAUTH2,
                oauth2_config=oauth2,
            )
            config.add_server("test", server_config)
            config.save()
            
            # Load config
            loaded_config = MCPAuthConfig.load(config_path)
            assert "test" in loaded_config.servers
            assert loaded_config.servers["test"].url == "http://test.nuxeo.com"
            assert loaded_config.servers["test"].auth_method == AuthMethod.OAUTH2
            # Client secret should be empty when loaded without env var
            assert loaded_config.servers["test"].oauth2_config.client_secret == ""


class TestOAuth2Token:
    """Test OAuth2 token handling."""
    
    def test_token_creation(self):
        """Test creating an OAuth2 token."""
        token = OAuth2Token(
            access_token="access-123",
            refresh_token="refresh-456",
            expires_in=3600,
        )
        assert token.access_token == "access-123"
        assert token.refresh_token == "refresh-456"
        assert token.expires_at is not None
    
    def test_token_expiration_check(self):
        """Test checking if token is expired."""
        import time
        
        # Create expired token
        token = OAuth2Token(
            access_token="access-123",
            expires_at=time.time() - 100,  # Expired 100 seconds ago
        )
        assert token.is_expired()
        
        # Create valid token
        token = OAuth2Token(
            access_token="access-456",
            expires_at=time.time() + 3600,  # Expires in 1 hour
        )
        assert not token.is_expired()
    
    def test_token_serialization(self):
        """Test token serialization and deserialization."""
        token = OAuth2Token(
            access_token="access-123",
            refresh_token="refresh-456",
            token_type="Bearer",
            expires_in=3600,
            scope="openid profile",
        )
        
        # Serialize
        data = token.to_dict()
        assert data["access_token"] == "access-123"
        assert data["refresh_token"] == "refresh-456"
        
        # Deserialize
        restored = OAuth2Token.from_dict(data)
        assert restored.access_token == token.access_token
        assert restored.refresh_token == token.refresh_token
        assert restored.scope == token.scope


class TestEncryptedFileStorage:
    """Test encrypted file token storage."""
    
    def test_store_and_retrieve_token(self):
        """Test storing and retrieving tokens."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = EncryptedFileStorage(Path(tmpdir))
            
            token = OAuth2Token(
                access_token="test-access",
                refresh_token="test-refresh",
            )
            
            # Store token
            storage.store_token("http://test.nuxeo.com", token)
            
            # Retrieve token
            retrieved = storage.get_token("http://test.nuxeo.com")
            assert retrieved is not None
            assert retrieved.access_token == "test-access"
            assert retrieved.refresh_token == "test-refresh"
    
    def test_delete_token(self):
        """Test deleting tokens."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = EncryptedFileStorage(Path(tmpdir))
            
            token = OAuth2Token(access_token="test-access")
            storage.store_token("http://test.nuxeo.com", token)
            
            # Delete token
            storage.delete_token("http://test.nuxeo.com")
            
            # Should return None now
            retrieved = storage.get_token("http://test.nuxeo.com")
            assert retrieved is None
    
    def test_list_servers(self):
        """Test listing servers with stored tokens."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = EncryptedFileStorage(Path(tmpdir))
            
            # Store tokens for multiple servers
            token1 = OAuth2Token(access_token="access1")
            token2 = OAuth2Token(access_token="access2")
            
            storage.store_token("http://server1.com", token1)
            storage.store_token("http://server2.com", token2)
            
            servers = storage.list_servers()
            assert len(servers) == 2
            assert "http://server1.com" in servers
            assert "http://server2.com" in servers


class TestTokenManager:
    """Test high-level token management."""
    
    def test_store_and_get_token(self):
        """Test storing and retrieving tokens via manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Force encrypted file backend
            manager = TokenManager(backend="encrypted_file")
            manager.storage = EncryptedFileStorage(Path(tmpdir))
            
            token_data = {
                "access_token": "access-123",
                "refresh_token": "refresh-456",
                "expires_in": 3600,
            }
            
            # Store token
            manager.store_token("http://test.com", token_data)
            
            # Get token
            retrieved = manager.get_token("http://test.com")
            assert retrieved is not None
            assert retrieved["access_token"] == "access-123"
    
    def test_expired_token_returns_none(self):
        """Test that expired tokens return None."""
        import time
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TokenManager(backend="encrypted_file")
            manager.storage = EncryptedFileStorage(Path(tmpdir))
            
            # Store expired token
            token_data = {
                "access_token": "expired-token",
                "expires_at": time.time() - 100,  # Expired
            }
            manager.store_token("http://test.com", token_data)
            
            # Should return None for expired token
            retrieved = manager.get_token("http://test.com")
            assert retrieved is None


class TestBasicAuthHandler:
    """Test basic authentication handler."""
    
    @patch('nuxeo_mcp.auth.Nuxeo')
    def test_basic_auth_success(self, mock_nuxeo_class):
        """Test successful basic authentication."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "testuser"}
        mock_client.client.request.return_value = mock_response
        mock_nuxeo_class.return_value = mock_client
        
        config = NuxeoServerConfig(
            url="http://test.com",
            auth_method=AuthMethod.BASIC,
            username="user",
            password="pass",
        )
        
        handler = BasicAuthHandler(config)
        result = handler.authenticate()
        
        assert result is True
        assert handler.nuxeo_client is not None
        mock_nuxeo_class.assert_called_with(
            host="http://test.com",
            auth=("user", "pass"),
        )
    
    @patch('nuxeo_mcp.auth.Nuxeo')
    def test_basic_auth_failure(self, mock_nuxeo_class):
        """Test failed basic authentication."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_client.client.request.return_value = mock_response
        mock_nuxeo_class.return_value = mock_client
        
        config = NuxeoServerConfig(
            url="http://test.com",
            auth_method=AuthMethod.BASIC,
            username="user",
            password="wrong",
        )
        
        handler = BasicAuthHandler(config)
        result = handler.authenticate()
        
        assert result is False


class TestAuthMiddleware:
    """Test authentication middleware."""
    
    def test_require_auth_decorator(self):
        """Test the require_auth decorator."""
        mock_handler = MagicMock()
        mock_handler.authenticate.return_value = True
        mock_handler.get_nuxeo_client.return_value = MagicMock()
        
        middleware = AuthMiddleware(mock_handler)
        
        @middleware.require_auth
        def protected_function():
            return "success"
        
        result = protected_function()
        assert result == "success"
        mock_handler.authenticate.assert_called_once()
    
    def test_logout(self):
        """Test logout functionality."""
        mock_handler = MagicMock()
        middleware = AuthMiddleware(mock_handler)
        
        middleware.logout()
        
        assert middleware._authenticated is False
        assert middleware._last_auth_check is None
        mock_handler.logout.assert_called_once()


class TestAuthenticationManager:
    """Test authentication manager."""
    
    @patch('nuxeo_mcp.middleware.OAuth2AuthHandler')
    def test_setup_oauth2(self, mock_oauth2_handler):
        """Test setting up OAuth2 authentication."""
        oauth2_config = OAuth2Config(
            client_id="test-client",
            client_secret="test-secret",
        )
        server_config = NuxeoServerConfig(
            url="http://test.com",
            auth_method=AuthMethod.OAUTH2,
            oauth2_config=oauth2_config,
        )
        
        manager = AuthenticationManager()
        result = manager.setup(server_config)
        
        assert result is True
        assert manager.auth_handler is not None
        assert manager.middleware is not None
        mock_oauth2_handler.assert_called_once_with(server_config)
    
    @patch('nuxeo_mcp.middleware.BasicAuthHandler')
    def test_setup_basic_auth(self, mock_basic_handler):
        """Test setting up basic authentication."""
        server_config = NuxeoServerConfig(
            url="http://test.com",
            auth_method=AuthMethod.BASIC,
            username="user",
            password="pass",
        )
        
        manager = AuthenticationManager()
        result = manager.setup(server_config)
        
        assert result is True
        assert manager.auth_handler is not None
        assert manager.middleware is not None
        mock_basic_handler.assert_called_once_with(server_config)