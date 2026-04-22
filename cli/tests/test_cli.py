from unittest.mock import AsyncMock, MagicMock, patch

from kosatka_cli.main import app
from typer.testing import CliRunner

runner = CliRunner()


def test_login():
    with patch("kosatka_cli.config.save_config") as mock_save:
        result = runner.invoke(app, ["login", "test-api-key", "--base-url", "http://test.com"])
        assert result.exit_code == 0
        assert "Successfully saved configuration" in result.stdout
        mock_save.assert_called_once()


def test_info():
    with patch("kosatka_cli.config.load_config") as mock_load:
        mock_load.return_value = MagicMock(base_url="http://test.com", api_key="test-key")
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Base URL: http://test.com" in result.stdout


def test_deploy_all():
    with patch("subprocess.run") as mock_run:
        result = runner.invoke(app, ["deploy", "all"])
        assert result.exit_code == 0
        assert "Running deployment" in result.stdout
        mock_run.assert_called_once()


def test_nodes_list():
    with patch("kosatka_cli.nodes.APIClient") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.list_nodes = AsyncMock(
            return_value=[
                {
                    "id": 1,
                    "name": "Node 1",
                    "address": "1.1.1.1",
                    "status": "online",
                    "provider_type": "agent",
                }
            ]
        )

        result = runner.invoke(app, ["nodes", "list"])
        assert result.exit_code == 0
        assert "Node 1" in result.stdout
        assert "1.1.1.1" in result.stdout


def test_doctor():
    with (
        patch("kosatka_cli.doctor.load_config") as mock_load,
        patch("httpx.AsyncClient.get") as mock_get,
        patch("kosatka_cli.doctor.APIClient") as mock_api_cls,
    ):

        mock_load.return_value = MagicMock(base_url="http://test.com", api_key="test-key")
        mock_get.return_value = MagicMock(status_code=200)
        mock_api = mock_api_cls.return_value
        mock_api.get_stats = AsyncMock(return_value={})

        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "✓ API Key found" in result.stdout
        assert "✓ Master is reachable" in result.stdout
        assert "✓ API authentication successful" in result.stdout
