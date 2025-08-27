# Document Template

**Category**: Template | **Status**: Published | **Version**: 0.9.0 | **Last Updated**: 2025-08-07

This is the standard template for all FLEXT documentation. Copy this template and customize it for your specific document.

## Frontmatter (Required)

Add this frontmatter at the top of every document:

```yaml
---
title: "Your Document Title"
description: "Brief description of what this document covers"
category: "getting-started|user-guides|developer|reference|standards"
status: "draft|review|published|deprecated"
version: "0.9.0"
last_updated: "YYYY-MM-DD"
contributors: ["author1", "author2"]
dependencies: ["related-doc-1", "related-doc-2"]
---
```

## Document Structure

```markdown
# Document Title

**Category**: [Category] | **Status**: [Status] | **Version**: [Version] | **Last Updated**: [Date]

Brief description of what this document covers and who it's for.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Main Section 1](#main-section-1)
- [Main Section 2](#main-section-2)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Related Documentation](#related-documentation)

## Overview

Provide a clear overview of what this document covers, why it's important, and what the reader will learn.

### What You'll Learn

- Key concept 1
- Key concept 2
- Key concept 3

### Who This Is For

- Target audience 1
- Target audience 2
- Prerequisites for understanding

## Prerequisites

List any requirements or knowledge needed before reading this document:

- **Required Knowledge**: What the reader should already know
- **Required Software**: Any software or tools needed
- **Required Access**: Any permissions or access needed
- **Related Documentation**: Documents that should be read first

## Main Section 1

### Subsection 1.1

Content here with clear explanations and examples.

### Subsection 1.2

More content with proper formatting:

- **Important Point**: Use bold for emphasis
- `Code Example`: Use code formatting for technical terms
- Regular text for normal content

## Main Section 2

### Subsection 2.1

Include code examples when relevant:

```python
# Example code with clear comments
def example_function():
    """Docstring explaining the function."""
    # Implementation with comments
    result = process_data()
    return result
```

### Subsection 2.2

Include configuration examples:

```yaml
# Configuration example
setting:
  key: value
  nested:
    subkey: subvalue
```

## Examples

Provide practical examples that show real-world usage:

### Example 1: Basic Usage

```python
# Basic example
from flext import FlextClient

client = FlextClient()
result = client.connect()
```

### Example 2: Advanced Usage

```python
# Advanced example with error handling
from flext import FlextClient, FlextExceptions.Error

try:
    client = FlextClient(config_path="config.yaml")
    result = client.process_data()
except FlextExceptions.Error as e:
    print(f"Error: {e}")
```

## Troubleshooting

Address common issues and their solutions:

### Common Issue 1

**Problem**: Description of the problem

**Solution**: Step-by-step solution

**Prevention**: How to avoid this issue

### Common Issue 2

**Problem**: Another common problem

**Solution**: Solution with code example

```bash
# Command to fix the issue
flext --fix-issue
```

## Related Documentation

- [Related Document 1](./related-doc-1.md) - Brief description
- [Related Document 2](./related-doc-2.md) - Brief description
- [External Resource](https://example.com) - External reference

## Next Steps

Suggest what the reader should do next:

1. **Read**: [Next Document](./next-doc.md)
2. **Try**: Practice with the examples
3. **Explore**: [Related Topic](./related-topic.md)

---

**Contributors**: [List of contributors]  
**Last Updated**: [Date]  
**Version**: [Version]

```

## Template Usage Guidelines

### When to Use This Template

- **New Documentation**: All new documents should use this template
- **Document Updates**: When significantly updating existing documents
- **Document Migration**: When moving documents to the new structure

### Customization Guidelines

1. **Keep the Structure**: Maintain the overall structure and sections
2. **Adapt Content**: Customize content for your specific topic
3. **Add Sections**: Add relevant sections as needed
4. **Remove Sections**: Remove sections that don't apply
5. **Maintain Standards**: Follow all documentation standards

### Required Elements

Every document must include:
- ✅ Frontmatter with all required fields
- ✅ Standardized header with metadata
- ✅ Clear overview and purpose
- ✅ Prerequisites section
- ✅ Related documentation links
- ✅ Footer with contributors and version

### Optional Elements

Elements that can be added as needed:
- Table of contents (for documents >500 words)
- Code examples
- Troubleshooting section
- Next steps section
- Diagrams or illustrations

## Related Documentation

- [Documentation Standards](./README.md) - Complete standards guide
- [Writing Guide](./writing-guide.md) - Detailed writing guidelines
- [Style Guide](./style-guide.md) - Visual and formatting standards

---

**Contributors**: FLEXT Documentation Team  
**Last Updated**: 2025-08-07  
**Version**: 0.9.0
