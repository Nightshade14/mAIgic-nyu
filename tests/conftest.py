import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def load_env():
    """Load environment variables before each test"""
    load_dotenv()