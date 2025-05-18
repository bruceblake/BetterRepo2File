# AI Action Block Schemas

This document defines the standardized action block formats used by BetterRepo2File to communicate structured information to downstream AI agents.

## Overview

Action blocks are structured data elements that can be parsed by AI agents for automated reasoning and decision-making. They appear in the generated output as specially formatted text blocks that maintain human readability while being machine-parseable.

## Schema Definitions

### 1. CALL_GRAPH_NODE

Represents a node in the call graph, showing function/method relationships.

```
[CALL_GRAPH_NODE file="path/to/file.py" entity="ClassName.method_name" type="method" calls="['Module.func1', 'ClassName.method2']" called_by="['Module.main', 'TestClass.test_method']"]
```

**Fields:**
- `file`: Relative path to the file containing the entity
- `entity`: Fully qualified name of the entity
- `type`: Entity type (function, method, class)
- `calls`: JSON array of entities this node calls
- `called_by`: JSON array of entities that call this node

### 2. GIT_INSIGHT

Provides Git history and contributor information for files.

```
[GIT_INSIGHT file="path/to/file.py" last_mod_date="2024-01-15" last_mod_author="jane.doe" last_commit="Added error handling" commit_hash="abc123" change_frequency_90d="12" recent_contributors="['jane.doe', 'john.smith']"]
```

**Fields:**
- `file`: Relative path to the file
- `last_mod_date`: Date of last modification (YYYY-MM-DD)
- `last_mod_author`: Username of last modifier
- `last_commit`: Last commit message
- `commit_hash`: Git commit hash (abbreviated)
- `change_frequency_90d`: Number of commits in last 90 days
- `recent_contributors`: JSON array of recent contributor usernames

### 3. TODO_ITEM

Identifies TODO comments in the codebase.

```
[TODO_ITEM file="path/to/file.py" line="42" type="TODO" text="Implement caching mechanism" priority="medium"]
```

**Fields:**
- `file`: Relative path to the file
- `line`: Line number where the TODO appears
- `type`: Type of marker (TODO, FIXME, HACK, NOTE)
- `text`: The TODO comment text
- `priority`: Inferred priority (high, medium, low)

### 4. PCA_NOTE

Proactive Context Augmentation notes from LLM analysis.

```
[PCA_NOTE type="ambiguity" file="path/to/file.py" lines="100-150" text="The error handling in this section may be incomplete" confidence="0.8"]
```

**Fields:**
- `type`: Type of note (ambiguity, assumption, suggestion, clarification)
- `file`: Relative path to the file
- `lines`: Line range for the relevant code section
- `text`: The analysis or suggestion text
- `confidence`: LLM confidence score (0.0-1.0)

### 5. CODE_QUALITY_METRIC

Objective code quality measurements.

```
[CODE_QUALITY_METRIC file="path/to/file.py" entity="ClassName.method_name" metric="cyclomatic_complexity" value="15" threshold="10" severity="warning"]
```

**Fields:**
- `file`: Relative path to the file
- `entity`: Entity being measured (file, class, method)
- `metric`: Metric name (cyclomatic_complexity, loc, lloc, maintainability_index)
- `value`: Numeric value of the metric
- `threshold`: Recommended threshold for this metric
- `severity`: Severity level if threshold exceeded (info, warning, error)

## Usage Examples

### Inline in Output Files

Action blocks can appear inline within the processed output files:

```python
# path/to/module.py

[GIT_INSIGHT file="path/to/module.py" last_mod_date="2024-01-15" last_mod_author="jane.doe" last_commit="Refactored data processing" commit_hash="abc123" change_frequency_90d="5" recent_contributors="['jane.doe', 'john.smith']"]

import numpy as np
from typing import List, Dict

[CODE_QUALITY_METRIC file="path/to/module.py" entity="DataProcessor.process" metric="cyclomatic_complexity" value="12" threshold="10" severity="warning"]

class DataProcessor:
    def process(self, data: List[Dict]) -> np.ndarray:
        [TODO_ITEM file="path/to/module.py" line="10" type="TODO" text="Add input validation" priority="high"]
        # TODO: Add input validation
        
        [CALL_GRAPH_NODE file="path/to/module.py" entity="DataProcessor.process" type="method" calls="['numpy.array', 'DataProcessor._validate']" called_by="['main', 'TestDataProcessor.test_process']"]
        
        result = np.array(data)
        return self._validate(result)
```

### In Manifest Section

Action blocks can also be aggregated in a dedicated section of the manifest:

```
## AI Action Blocks Summary

### High Priority Items
[TODO_ITEM file="src/auth.py" line="45" type="FIXME" text="Security vulnerability in token validation" priority="high"]
[CODE_QUALITY_METRIC file="src/database.py" entity="DatabaseManager.execute_query" metric="cyclomatic_complexity" value="25" threshold="10" severity="error"]

### Code Quality Warnings
[CODE_QUALITY_METRIC file="src/api.py" entity="APIHandler.handle_request" metric="maintainability_index" value="45" threshold="65" severity="warning"]

### Architecture Insights
[CALL_GRAPH_NODE file="src/core.py" entity="CoreEngine.run" type="method" calls="['DatabaseManager.connect', 'APIHandler.start', 'Logger.initialize']" called_by="['main']"]
```

## Configuration

Action block generation can be configured in the ProcessingProfile:

```json
{
  "enable_action_blocks": true,
  "action_block_format": "inline",  // or "manifest", or "both"
  "action_block_types": [
    "CALL_GRAPH_NODE",
    "GIT_INSIGHT",
    "TODO_ITEM",
    "PCA_NOTE",
    "CODE_QUALITY_METRIC"
  ],
  "action_block_filters": {
    "min_complexity": 10,
    "min_priority": "medium",
    "include_private_methods": false
  }
}
```

## Best Practices

1. **Consistency**: Always use the exact field names and formats specified
2. **Completeness**: Include all required fields for each block type
3. **Context**: Place inline blocks near the relevant code sections
4. **Aggregation**: Summarize high-priority items in the manifest
5. **Filtering**: Use configuration to control the volume of blocks generated

## Integration Guide for AI Agents

To parse action blocks in your AI agent:

1. Use regex pattern: `\[([A-Z_]+)\s+([^\]]+)\]`
2. Parse the captured groups to extract block type and fields
3. Convert JSON arrays in field values where appropriate
4. Build internal data structures based on block types
5. Use the structured data for:
   - Task prioritization
   - Code navigation
   - Quality assessment
   - Refactoring suggestions
   - Security analysis

## Future Extensions

The action block system is designed to be extensible. New block types can be added by:

1. Defining the schema in this document
2. Implementing the generation logic in the appropriate analyzer
3. Adding configuration options to ProcessingProfile
4. Updating the integration logic in dump_ultra.py