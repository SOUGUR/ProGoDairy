# Import Style Guide

We follow the standard Python import order (PEP 8 recommendations) with `isort` style grouping.

## Order of Imports

1.  **Standard Library Imports**: Built-in Python modules (e.g., `os`, `sys`, `typing`, `datetime`).
2.  **Third-Party Imports**: External libraries installed via pip (e.g., `django`, `strawberry`, `rest_framework`).
3.  **Local Application Imports**: Modules from this project (e.g., `dairy_project`, `suppliers`, `milk`).

## Formatting Rules

*   **Alphabetical Order**: Imports within each group should be sorted alphabetically.
*   **Grouping**: Separate each group with a single blank line.
*   **Absolute Imports**: Prefer absolute imports over relative imports for clarity, except for sibling modules within the same package where explicit relative imports (e.g., `from . import models`) are acceptable.
*   **Multi-line Imports**: Use parentheses `()` for multi-line imports.

## Example

```python
# 1. Standard Library
from datetime import datetime
from typing import List, Optional

# 2. Third-Party
import strawberry
from django.db import models

# 3. Local Application
from dairy_project.graphql_types.auth import UserType
from suppliers.models import Supplier
```

## GraphQL Types

When importing GraphQL types from `dairy_project.graphql_types`, always import from the specific submodule to avoid circular dependencies and keep imports clean.

**Correct:**
```python
from dairy_project.graphql_types.milk import MilkLotType
```

**Incorrect:**
```python
from dairy_project.graphql_types import MilkLotType
```
