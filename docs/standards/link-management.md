# Link Management and Cross-Reference Procedures

**Version**: 1.0  
**Last Updated**: 2025-12-07  
**Status**: Active

## Overview

This document defines the standards and procedures for managing links and
cross-references across the FLEXT ecosystem documentation. It ensures
consistency, maintainability, and accuracy of all documentation links.

## Link Reference Standards

### Link Types and Patterns

#### 1. Same Project (Internal References)

**Use relative paths** for references within the same project:

```markdown
✅ CORRECT - Relative paths within project

- [Getting Started](./getting-started.md)
- [Architecture Overview](../architecture/overview.md)
- [API Reference](./api-reference/foundation.md)

❌ WRONG - GitHub URLs within project

- [Getting Started](https://github.com/organization/flext/tree/main/flext-core/docs/getting-started.md)
```

**Rationale**:

- Works in local development environment
- Faster (no external HTTP requests)
- Works offline
- Survives repository moves/renames

#### 2. Cross-Project References (Between FLEXT Projects)

**Use GitHub URLs** for cross-project references:

```markdown
✅ CORRECT - GitHub URLs for cross-project

- [flext-core Foundation](https://github.com/organization/flext/tree/main/flext-core/docs/architecture/overview.md)
- [flext-ldif Processing](https://github.com/organization/flext/tree/main/flext-ldif/docs/architecture.md)

❌ WRONG - Relative paths for cross-project

- [flext-core](../../flext-core/docs/architecture/overview.md)
```

**Rationale**:

- GitHub URLs remain valid when viewing individual project repos
- Works across different repository setups (monorepo, separate repos)
- Consistent regardless of workspace organization

#### 3. Workspace Documentation

**Use relative paths from root** for workspace-level documentation:

```markdown
✅ CORRECT - Relative from root

- [Workspace Documentation](../../docs/index.md)
- [FLEXT Standards](../../AGENTS.md)

❌ WRONG - GitHub URLs for workspace docs

- [Workspace Documentation](https://github.com/organization/flext/tree/main/docs/index.md)
```

#### 4. External Resources

**Use full HTTPS URLs** for external references:

```markdown
✅ CORRECT - Full HTTPS URLs

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

❌ WRONG - HTTP or incomplete URLs

- [PEP 257](http://peps.python.org/pep-0257/)
- [Google Style](google.github.io/styleguide/pyguide.html)
```

## "Related Documentation" Section Pattern

### Standard Structure

All major documentation files must include a "Related Documentation" section at the end following this pattern:

```markdown
## Related Documentation

**Within Project**:

- [Getting Started](getting-started.md) - Installation and basic usage
- [Architecture](architecture.md) - Architecture and design patterns
- [API Reference](api-reference.md) - Complete API documentation

**Across Projects**:

- [flext-core
  Foundation](https://github.com/organization/flext/tree/main/flext-core/docs/architecture/overview.md)
  - Clean architecture and CQRS patterns
- [flext-core Service
  Patterns](https://github.com/organization/flext/tree/main/flext-core/docs/guides/service-patterns.md)
  - Service patterns and dependency injection

**External Resources**:

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
```

### Section Guidelines

1. **Within Project**: List 3-5 most relevant internal documentation files
2. **Across Projects**: List 2-4 most relevant cross-project references (use GitHub URLs)
3. **External Resources**: List 2-3 authoritative external references (RFCs, style guides, etc.)

### When to Add

Add "Related Documentation" sections to:

- ✅ All `getting-started.md` files
- ✅ All `architecture.md` files
- ✅ All `api-reference.md` files
- ✅ Major guide files (e.g., `railway-oriented-programming.md`)
- ❌ Not needed for: README files, small utility docs, changelogs

## Bidirectional Links

### Principle

When document A references document B, consider adding a reciprocal reference in
document B to document A where it makes sense contextually.

### Guidelines

1. **Not Always Required**: Bidirectional links should be contextually relevant, not forced
2. **Natural Flow**: Add reciprocal links only when they add value to the reader
3. **Avoid Circular References**: Don't create circular link chains
4. **Focus on Key Relationships**: Prioritize bidirectional links for:
   - Core foundation patterns (flext-core ↔ project-specific implementations)
   - Complementary services (flext-ldap ↔ flext-ldif)
   - Integration patterns (flext-meltano ↔ flext-plugin)

### Example

**Document A** (`flext-ldif/docs/getting-started.md`):

```markdown
**Across Projects**:

- [flext-core Foundation](https://github.com/organization/flext/tree/main/flext-core/docs/architecture/overview.md)
```

**Document B** (`flext-core/docs/architecture/overview.md`):

```markdown
**Across Projects**:

- [flext-ldif Processing](https://github.com/organization/flext/tree/main/flext-ldif/docs/getting-started.md)
```

## Link Update Procedures

### When Adding New Documentation

1. **Create the new document** following the standard structure
2. **Add "Related Documentation" section** at the end
3. **Update related documents** to include links to the new document
4. **Verify all links** resolve correctly

### When Moving or Renaming Files

1. **Update all internal links** in the same project
2. **Update cross-project links** in other projects (use GitHub URLs)
3. **Check for broken links** using link validation tools
4. **Update "Related Documentation" sections** in affected files

### When Removing Documentation

1. **Remove the file** (or rename to `.bak` for audit trail)
2. **Remove all links** to the deleted file
3. **Update "Related Documentation" sections** in related files
4. **Document the removal** in changelog or migration guide

### Regular Maintenance

1. **Weekly Link Validation**: Run automated link checking
2. **Quarterly Review**: Audit all cross-project links
3. **Version Updates**: Update version references in links
4. **External Link Monitoring**: Check external links for availability

## Link Validation

### Automated Validation

Use `flext-quality` tools for automated link validation:

```bash
# Validate all links in workspace
flext-docs validate_links --projects-root ~/flext

# Check specific project
flext-docs validate_links --projects-root ~/flext/flext-core
```

### Manual Validation Checklist

- [ ] All same-project links use relative paths
- [ ] All cross-project links use GitHub URLs
- [ ] All external links use HTTPS
- [ ] All links resolve correctly (no 404 errors)
- [ ] Anchor links (#sections) point to existing sections
- [ ] "Related Documentation" sections follow standard pattern

## Common Issues and Solutions

### Issue: Broken Internal Link

**Symptoms**: Link returns 404 or points to wrong file

**Solution**:

1. Verify file exists at target path
2. Check relative path calculation
3. Update link to correct path
4. Test link resolution

### Issue: Broken Cross-Project Link

**Symptoms**: GitHub link returns 404 or points to wrong location

**Solution**:

1. Verify file exists in target project
2. Check GitHub URL format: `https://github.com/organization/flext/tree/main/project/path/to/file.md`
3. Update link to correct GitHub URL
4. Test link in browser

### Issue: Missing "Related Documentation" Section

**Symptoms**: Major documentation file lacks cross-references

**Solution**:

1. Add "Related Documentation" section following standard pattern
2. Include relevant "Within Project", "Across Projects", and "External Resources"
3. Verify all links resolve correctly

### Issue: Inconsistent Link Patterns

**Symptoms**: Mix of relative paths and GitHub URLs for same link type

**Solution**:

1. Audit all links in file
2. Convert to correct pattern (relative for same-project, GitHub for cross-project)
3. Update all occurrences consistently

## Link Registry (Future Enhancement)

### Automated Registry

Consider implementing automated link registry using `flext-quality`:

```python
# Future: Automated link registry
from flext_quality import link_registry

# Register all links
registry = link_registry.scan_workspace("~/flext")

# Query links
links_to_flext_core = registry.find_links(target="flext-core")
broken_links = registry.find_broken_links()
```

### Manual Registry

For now, maintain awareness of key cross-project relationships:

- **flext-core** → Referenced by all projects
- **flext-ldap** ↔ **flext-ldif** (bidirectional)
- **flext-meltano** ↔ **flext-plugin** (bidirectional)
- **flext-db-oracle** → Referenced by Oracle-related projects

## Best Practices

### ✅ DO

- Use relative paths for same-project links
- Use GitHub URLs for cross-project links
- Include "Related Documentation" sections in major docs
- Verify links after any file moves or renames
- Keep cross-project links updated when projects change
- Use descriptive link text (not "click here")

### ❌ DON'T

- Mix relative paths and GitHub URLs for same link type
- Use absolute file system paths
- Create circular link chains
- Leave broken links unrepaired
- Use HTTP for external links (always HTTPS)
- Create overly long link lists (keep "Related Documentation" concise)

## Related Documentation

**Within Project**:

- [Documentation Standards](documentation.md) - General documentation standards
- [README](../README.md) - Standards overview

**Across Projects**:

- [flext-core Documentation
  Standards](https://github.com/organization/flext/tree/main/flext-core/docs/standards/documentation.md)
  - Core documentation patterns
- [FLEXT Workspace Documentation](../README.md) - Workspace-level documentation

**External Resources**:

- [Markdown Link Syntax](https://www.markdownguide.org/basic-syntax/#links)
- [GitHub Markdown Guide](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#links)

---

**Maintained By**: FLEXT Documentation Team  
**Last Review**: 2025-12-07  
**Next Review**: 2026-01-07
