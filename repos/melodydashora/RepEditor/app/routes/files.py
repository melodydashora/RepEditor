"""File tree API endpoint"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from pathlib import Path

router = APIRouter(prefix="/api/files", tags=["files"])


def build_tree(directory: str = ".", prefix: str = "") -> List[Dict[str, Any]]:
    """Build a tree structure of files and directories (matching Replit behavior)"""
    items = []
    try:
        paths = sorted(Path(directory).iterdir(), key=lambda p: (not p.is_dir(), p.name))
        
        for path in paths:
            # Only skip large build artifacts and version control
            # Show hidden files (like .env, .replit, etc.) to match Replit's file tree
            if path.name in ['__pycache__', 'node_modules', '.git', 'venv', '.venv', 'dist', 'build']:
                continue
            
            item = {
                "name": path.name,
                "path": str(path),
                "type": "directory" if path.is_dir() else "file",
                "children": []
            }
            
            if path.is_dir():
                item["children"] = build_tree(str(path), prefix + "  ")
            
            items.append(item)
    except Exception:
        pass
    
    return items


@router.get("/tree")
async def get_file_tree():
    """Get the complete repository file tree"""
    return build_tree(".")
