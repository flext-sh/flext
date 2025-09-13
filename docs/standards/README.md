# FLEXT Documentation Standards

**Category**: Standards | **Status**: Published | **Version**: 0.9.0 | **Last Updated**: 2025-08-07

This document defines the standards and guidelines for all FLEXT documentation to ensure consistency, quality, and professionalism across the entire documentation ecosystem.

## Table of Contents

- [Overview](#overview)
- [Document Structure](#document-structure)
- [Content Standards](#content-standards)
- [Writing Guidelines](#writing-guidelines)
- [Code Examples](#code-examples)
- [Navigation Standards](#navigation-standards)
- [Quality Checklist](#quality-checklist)

## Overview

FLEXT documentation follows a structured approach to ensure:

- **Consistency** across all documents
- **Professionalism** in presentation and language
- **Usability** for different types of users
- **Maintainability** for long-term sustainability
- **Reality-based** content that matches actual implementation

## Document Structure

### Required Frontmatter

Every document must include standardized frontmatter:

```yaml
---
title: "Document Title"
description: "Brief description of the document"
category: "getting-started|user-guides|developer|reference|standards"
status: "draft|review|published|deprecated"
version: "0.9.0"
last_updated: "YYYY-MM-DD"
contributors: ["author1", "author2"]
dependencies: ["related-doc-1", "related-doc-2"]
---
```

### Document Header

Every document must have a standardized header:

```markdown
# Document Title

**Category**: [Category] | **Status**: [Status] | **Version**: [Version] | **Last Updated**: [Date]

Brief description of what this document covers and who it's for.
```

### Required Sections

1. **Table of Contents** - For documents longer than 500 words
2. **Overview/Introduction** - Clear purpose and scope
3. **Main Content** - Organized with clear headings
4. **Related Documentation** - Links to related content
5. **Footer** - Contributors, last updated, version

## Content Standards

### Reality-Based Documentation

✅ **Do:**

- Document actual implementation status
- Include working code examples
- Specify clear prerequisites and dependencies
- Acknowledge limitations and known issues
- Update documentation when implementation changes

❌ **Don't:**

- Make marketing claims or fictional achievements
- Include outdated or incorrect information
- Promise features that don't exist
- Hide known problems or limitations

### Professional Language

✅ **Do:**

- Use clear, concise, and technical language
- Maintain consistent terminology across all documents
- Use proper grammar and spelling
- Write in active voice when possible
- Define technical terms on first use

❌ **Don't:**

- Use informal or marketing language
- Use technical jargon without explanation
- Write in passive voice unnecessarily
- Use abbreviations without defining them

### Accuracy and Completeness

✅ **Do:**

- Verify all information before publishing
- Include version numbers and compatibility notes
- Test all code examples
- Provide complete step-by-step instructions
- Include troubleshooting information

❌ **Don't:**

- Publish incomplete or untested information
- Assume reader knowledge
- Skip important steps in procedures
- Leave out error handling information

## Writing Guidelines

### Document Organization

1. **Start with the goal** - What will the reader accomplish?
2. **Provide context** - Why is this information important?
3. **Give step-by-step instructions** - How to achieve the goal?
4. **Include examples** - Show real-world usage
5. **Address common issues** - What might go wrong?

### Heading Structure

- **H1 (#)** - Document title only
- **H2 (##)** - Major sections
- **H3 (###)** - Subsections
- **H4 (####)** - Minor subsections (use sparingly)

### Lists and Formatting

- Use bullet points for unordered lists
- Use numbered lists for step-by-step procedures
- Use bold for emphasis on important terms
- Use code formatting for technical terms, commands, and file names
- Use blockquotes for warnings, notes, and tips

### Links and References

- Use relative links for internal documentation
- Include descriptive link text
- Verify all links work before publishing
- Use anchor links for specific sections

## Code Examples

### Code Block Standards

````markdown
```python
# Clear, descriptive comment
def example_function():
    """Docstring explaining the function."""
    # Implementation with comments
    result = process_data()
    return result
```
````

### Code Example Requirements

✅ **Do:**

- Include working, tested code
- Add clear comments and explanations
- Use proper syntax highlighting
- Include error handling where relevant
- Show complete, runnable examples
- Include expected output when helpful

❌ **Don't:**

- Include pseudo-code or incomplete examples
- Use placeholder text like "TODO" or "FIXME"
- Skip error handling in production code
- Assume the reader knows the context

### Code Style

- Follow language-specific style guides (PEP 8 for Python, etc.)
- Use consistent indentation and formatting
- Include type hints where appropriate
- Add docstrings for functions and classes

## Navigation Standards

### Directory Structure

Every directory must have a `README.md` that includes:

- Overview of the directory's purpose
- List of documents with brief descriptions
- Navigation guidance for users
- Related directories and resources

### Cross-References

- Use relative paths for internal links
- Include anchor links for specific sections
- Maintain a "Related Documentation" section
- Update links when documents are moved or renamed

### Search and Discovery

- Use descriptive file names
- Include relevant keywords in content
- Create indexes
- Use consistent terminology for searchability

## Quality Checklist

Before publishing any document, verify:

### Content Quality

- [ ] Information is accurate and up-to-date
- [ ] Code examples work and are tested
- [ ] All links are valid and working
- [ ] No marketing claims or fictional content
- [ ] Prerequisites and dependencies are clearly stated

### Structure and Format

- [ ] Document follows the standard template
- [ ] Frontmatter is complete and correct
- [ ] Table of contents is included (if needed)
- [ ] Headings follow the hierarchy guidelines
- [ ] Related documentation links are included

### Language and Style

- [ ] Professional language throughout
- [ ] Consistent terminology used
- [ ] No spelling or grammar errors
- [ ] Technical terms are defined
- [ ] Active voice used where appropriate

### Navigation

- [ ] Document is in the correct directory
- [ ] Directory README is updated
- [ ] Cross-references are accurate
- [ ] File name is descriptive and consistent

## Templates

Standard templates are available in the `standards/templates/` directory:

- [Document Template](./templates/document-template.md)
- [API Reference Template](./templates/api-template.md)
- [User Guide Template](./templates/user-guide-template.md)
- [Developer Guide Template](./templates/developer-guide-template.md)

## Related Documentation

- [Writing Guide](./writing-guide.md) - Detailed writing guidelines
- [Style Guide](./style-guide.md) - Visual and formatting standards
- [Documentation Plan](../DOCUMENTATION_REORGANIZATION_PLAN.md) - Overall reorganization strategy

---

**Contributors**: FLEXT Documentation Team  
**Last Updated**: 2025-08-07  
**Version**: 0.9.0
