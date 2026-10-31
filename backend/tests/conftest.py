import pytest
from app.services.document_service import document_service


@pytest.fixture(autouse=True)
def clean_workspace_for_test():
    """Ensure a clean project workspace before and after each test."""
    document_service.reset_workspace()
    yield
    document_service.reset_workspace()
