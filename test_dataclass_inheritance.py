#!/usr/bin/env python3
"""Test dataclass inheritance to understand the issue"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum

class BlockType(Enum):
    TYPE_A = "A"
    TYPE_B = "B"

# Test 1: Basic inheritance
@dataclass
class BaseClass:
    """Base class test"""
    file: str
    block_type: BlockType = field(init=False)
    
print("Test 1: Basic inheritance")
try:
    @dataclass
    class ChildClass(BaseClass):
        """Child class test"""
        data: str
        
        def __post_init__(self):
            self.block_type = BlockType.TYPE_A
    
    child = ChildClass(file="test.py", data="some data")
    print(f"Success: {child.file}, {child.data}, {child.block_type}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: What happens with the GitInsight pattern
print("\nTest 2: GitInsight pattern")
try:
    @dataclass
    class GitInsightTest(BaseClass):
        last_mod_date: str
        last_mod_author: str
        
        def __post_init__(self):
            self.block_type = BlockType.TYPE_B
    
    # How GitInsight is actually called
    git = GitInsightTest(
        file="test.py",
        last_mod_date="2024-01-15",
        last_mod_author="author"
    )
    print(f"Success: {git.file}, {git.last_mod_date}, {git.block_type}")
except Exception as e:
    print(f"Error: {e}")