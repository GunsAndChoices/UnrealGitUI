import pytest
from unittest.mock import patch, mock_open
import os

from main.config import load_config, save_config, check_config
from main.errors import MissingDotEnvFile, MissingGithubToken

@pytest.fixture
def mock_env_file(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")

@pytest.fixture
def mock_missing_env_file(monkeypatch):
    if os.path.exists('main/.env'):
        os.remove('main/.env')

@pytest.fixture
def mock_json_file():
    return '{"git": {"token": ""}}'

def test_load_config_success(mock_env_file, mock_json_file):
    with patch("builtins.open", mock_open(read_data=mock_json_file)) as mock_file:
        with patch("os.path.exists", return_value=True):
            config = load_config("dummy_path")
            assert config["git"]["token"] == "test_token"
            mock_file.assert_called_with("dummy_path", "r")

def test_load_config_missing_env_file(mock_missing_env_file, mock_json_file):
    with patch("builtins.open", mock_open(read_data=mock_json_file)):
        with patch("os.path.exists", return_value=False):
            with pytest.raises(MissingDotEnvFile):
                load_config("dummy_path")

def test_load_config_missing_github_token(mock_json_file, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with patch("builtins.open", mock_open(read_data=mock_json_file)):
        with patch("os.path.exists", return_value=True):
            with patch("os.getenv", return_value=None):
                with pytest.raises(MissingGithubToken):
                    load_config("dummy_path")

def test_save_config(mock_json_file):
    config_to_save = {"git": {"token": "saved_token"}}
    with patch("builtins.open", mock_open()) as mock_file:
        save_config("dummy_path", config_to_save)
        mock_file.assert_called_with("dummy_path", "w")
        # In a real scenario, you'd also check the content written to the file
        # For example, by capturing the write calls.

def test_check_config_success(mock_env_file, mock_json_file):
    with patch("main.config.load_config", return_value={"git": {"token": "test_token"}}):
        assert check_config(["git"]) is True

def test_check_config_fail(mock_env_file, mock_json_file):
    with patch("main.config.load_config", return_value={"git": {"token": "test_token"}}):
        assert check_config(["non_existent_key"]) is False

