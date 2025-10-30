import pytest
import pdb
from utils.convenience import load_secrets

load_secrets()


def test_langsmith_connection(langsmith_client):
    try:
        projects = list(langsmith_client.list_projects())

        pdb.set_trace()
        assert projects is not None, (
            "No projects returned. Connection might not be established."
        )
        for project in projects:
            if project.name == "civic-assistant-team-5":
                print(f"Found project: {project.name} with ID: {project.id}")
                break
        else:
            pytest.fail("Project 'civic-assistant-team-5' not found.")
    except Exception as e:
        pytest.fail(f"Failed to connect to LangSmith: {e}")
