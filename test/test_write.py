import pytest
import os
from utils import save_summary  

# pytest test/test_write.py -v

@pytest.fixture
def cleanup():
    # Setup - nothing needed
    yield
    # Teardown - clean up the summaries directory
    if os.path.exists("summaries"):
        for file in os.listdir("summaries"):
            os.remove(os.path.join("summaries", file))
        os.rmdir("summaries")

def test_save_summary_default_filename(cleanup):
    content = "Test summary content"
    filepath = save_summary(content)
    
    # Check if file exists
    assert os.path.exists(filepath)
    assert filepath.startswith("summaries/summary_")
    assert filepath.endswith(".txt")
    
    # Check content
    with open(filepath, 'r', encoding='utf-8') as f:
        saved_content = f.read()
    assert saved_content == content

def test_save_summary_custom_filename(cleanup):
    content = "Test summary content"
    custom_filename = "my_summary.txt"
    filepath = save_summary(content, custom_filename)
    
    # Check if file exists with correct name
    assert os.path.exists(filepath)
    assert filepath == os.path.join("summaries", custom_filename)
    
    # Check content
    with open(filepath, 'r', encoding='utf-8') as f:
        saved_content = f.read()
    assert saved_content == content

def test_save_summary_adds_txt_extension(cleanup):
    content = "Test summary content"
    filename = "my_summary"  # No extension
    filepath = save_summary(content, filename)
    
    # Check if .txt was added
    assert filepath.endswith(".txt")
    assert os.path.exists(filepath)
