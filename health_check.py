"""
Adobe Hackathon Project Health Check
"""
import sys
from pathlib import Path

def health_check():
    print("=== Adobe Hackathon Project Health Check ===")
    
    # Check model size
    models_dir = Path("app/models/round1b/embedding_model")
    if models_dir.exists():
        total_size = sum(f.stat().st_size for f in models_dir.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        print(f" Model size: {size_mb:.1f} MB (under 1GB limit)")
    
    # Check outputs exist
    outline_files = list(Path("app/output").glob("*_outline.json"))
    collection_files = list(Path("collections").glob("*/challenge1b_output.json"))
    
    print(f" Round 1A outlines: {len(outline_files)} files")
    print(f" Round 1B outputs: {len(collection_files)} files")
    
    if outline_files and collection_files:
        print(" Project Status: COMPETITION READY")
    else:
        print("  Project Status: Run rounds 1A and 1B")

if __name__ == "__main__":
    health_check()
