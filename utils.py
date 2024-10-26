import os
from datetime import datetime

def save_summary(content: str, filename: str = None) -> str:
    """
    Save content to a local file in the summaries directory.
    
    Args:
        content: The text content to save
        filename: Optional custom filename, will generate timestamp-based one if None
    
    Returns:
        str: Path to the saved file
    """
    
    # Create summaries directory if it doesn't exist
    summary_dir = "summaries"
    os.makedirs(summary_dir, exist_ok=True)
    
    # Generate filename with timestamp if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.txt"
    
    # Ensure .txt extension
    if not filename.endswith('.txt'):
        filename += '.txt'
    
    filepath = os.path.join(summary_dir, filename)
    
    # Write content to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath