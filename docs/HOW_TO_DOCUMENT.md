# 📝 FLEXT Framework - Documentation Standards Guide

> **Regras do Projeto FLEXT**: Para padrões obrigatórios, consulte `.github/instructions/regras.instructions.md`

> **Complete guide for writing, maintaining, and organizing documentation in the FLEXT Framework ecosystem**

[![Documentation](https://img.shields.io/badge/docs-standardized-green.svg)](./index.md)
[![Standards](https://img.shields.io/badge/standards-PEP8-blue.svg)](./development/standardization-plan.md)
[![Templates](https://img.shields.io/badge/templates-unified-orange.svg)](./MANDATORY_COMPLIANCE_DIRECTIVE.md)

Essential guide for contributors, maintainers, and agents working on FLEXT Framework documentation

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](./index.md) → **📄 Current**: How to Document Guide

---

## 🎯 **Quick Links**

- **📂 Documentation Root**: [Main Index](./index.md)
- **🚨 Compliance Directive**: [Mandatory Standards](./MANDATORY_COMPLIANCE_DIRECTIVE.md)
- **🤝 Coordination**: [Agent Coordination](./STANDARDIZATION_MASTER_PLAN.md)

---

## 📋 **Documentation Philosophy**

### **Core Principles**

1. **🎯 User-Centric**: Documentation serves real user needs and workflows
2. **🏗️ Hierarchical**: Clear hub-based structure for optimal navigation
3. **🔗 Interconnected**: Rich cross-references between related concepts
4. **⚡ Actionable**: Every document should enable specific actions
5. **✅ Validated**: Documentation reflects actual code implementation

### **Quality Standards**

- **English Only**: All documentation in English for global accessibility
- **Current Content**: Focus on current implementation, remove obsolete content
- **Code Validation**: API docs validated against actual `/flext/src/` code
- **Professional Grade**: Enterprise-level documentation standards
- **Date Tracking**: All reorganized documents must include date 2025-06-11

---

## 🏗️ **Documentation Architecture**

### **Hierarchical Structure (MANDATORY)**

```
/docs/index.md (ROOT - ABSOLUTE NAVIGATION CENTER)
    ↓
[CATEGORY]/index.md (FUNCTIONAL HUBS)
    ↓
[CATEGORY]/document.md (SPECIALIZED CONTENT)
    ↓
Cross-references & Navigation
```

### **Functional Categories**

| **Category**         | **Function**             | **Audience**            | **Pattern**                              |
| -------------------- | ------------------------ | ----------------------- | ---------------------------------------- |
| **getting-started/** | Onboarding & first steps | New developers          | Tutorial → Config → Project              |
| **architecture/**    | Design & patterns        | Architects, senior devs | Overview → Components → Implementation   |
| **development/**     | Tools & dev standards    | Developers, teams       | Standards → Tools → Process              |
| **guides/**          | Practical tutorials      | Implementation devs     | Problem → Solution → Example             |
| **api-reference/**   | Complete API docs        | Implementation devs     | Overview → Modules → Classes → Functions |
| **integrations/**    | External integrations    | Integration engineers   | Overview → System → Configuration        |
| **optimization/**    | Performance tuning       | Performance engineers   | Analysis → Strategy → Implementation     |
| **ports/**           | Hexagonal architecture   | Framework developers    | Concepts → Implementation → Examples     |

---

## 📏 **Mandatory Templates**

### **🎯 Hub Template (index.md files)**

**Every hub MUST follow this exact template:**

```markdown
# [🎯 Icon] [Section Name] - Navigation Hub

> **Function**: [Specific function description] | **Audience**: [Target audience]

[![Relevant Badge](URL)](LINK)

**[One-line description of section and audience]**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../index.md) → **📂 Current Hub**: [Section Name]

## 🎯 **Quick Navigation**

### **Core Topics**

| **Topic**              | **Function**         | **Audience**    | **Status** |
| ---------------------- | -------------------- | --------------- | ---------- |
| [Topic 1](./topic1.md) | Function description | Target audience | ✅ Status  |
| [Topic 2](./topic2.md) | Function description | Target audience | 🔶 Status  |

### **📋 Learning Path**

1. **🎯 Start Here**: [First Document](./start.md) - What to read first
2. **⚡ Quick Path**: [Quick Guide](./quick.md) - Fast implementation
3. **📚 Deep Dive**: [Complete Guide](./complete.md) - Comprehensive coverage

---

## 🔗 **Cross-Section Navigation**

### **⬅️ Prerequisites**

- [Required Hub](../required/index.md) - Why needed before this section

### **➡️ Next Steps**

- [Next Hub](../next/index.md) - What comes after this section

### **🔗 Related Sections**

- [Related Hub 1](../related1/index.md) - Connection explanation
- [Related Hub 2](../related2/index.md) - Connection explanation

---

## 📊 **Section Metrics**

- **Documents**: X files
- **Completeness**: Y%
- **Last Updated**: Date

---

**📂 Section Hub** | **🏠 Parent**: [Documentation Root](../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
```

### **📄 Document Template (content files)**

**Every content document MUST follow this template:**

```markdown
# [Title] - [Category]

> **Function**: [Specific function] | **Audience**: [Target audience] | **Status**: [Stable|Beta|Deprecated]

[![Relevant Badge](URL)](LINK)

**[One-line description based on reality]**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Home](../index.md) → **📂 Hub**: [Section Hub](./index.md) → **📄 Current**: [Document Name]

### **📍 Learning Path Position**
```

[Previous Doc](./prev.md) → **[CURRENT]** → [Next Doc](./next.md)

```

## 🎯 **Quick Links**
- **📂 Section Hub**: [Hub Name](./index.md)
- **🏠 Documentation Root**: [Root Index](../index.md)
- **🔗 Related**: [Related Doc](./related.md)

---

## 📋 **Content Sections**

### **Overview**
[Brief overview of what this document covers]

### **Prerequisites**
- [Required knowledge/tools]
- [Dependencies that must be in place]

### **Main Content**
[Core content organized in logical sections]

### **Examples**
[Practical examples with code snippets]

### **Implementation**
[Step-by-step implementation guidance]

---

## 🔗 **Cross-References**

### **Prerequisites**
- [Required 1](./req1.md) - Why needed
- [Required 2](./req2.md) - Why needed

### **Next Steps**
- [Step 1](./step1.md) - What to do next
- [Step 2](./step2.md) - Alternative path

### **Related Topics**
- [Related 1](./rel1.md) - Connection explanation
- [Related 2](./rel2.md) - Connection explanation

---

## 🆘 **Troubleshooting**
[Common issues and solutions based on real problems]

---

**📂 Hub**: [Section Hub](./index.md) | **🏠 Root**: [Home](../index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
```

---

## 🎨 **Writing Style Guide**

### **Voice & Tone**

- **Clear & Direct**: Use simple, direct language
- **Action-Oriented**: Focus on what users can do
- **Professional**: Maintain enterprise-grade quality
- **Consistent**: Use established terminology throughout

### **Structure Patterns**

1. **Start with Purpose**: Every document begins with clear purpose
2. **Progressive Disclosure**: Simple to complex information flow
3. **Actionable Sections**: Each section enables specific actions
4. **Concrete Examples**: Real code examples, not pseudocode
5. **Clear Navigation**: Always provide clear next steps

### **Language Standards**

- **English Only**: All content in English
- **Present Tense**: Use present tense for actions
- **Active Voice**: Prefer active over passive voice
- **Consistent Terminology**: Use framework terminology consistently

---

## 🔗 **Cross-Reference System**

### **Reference Types (MANDATORY)**

Every document MUST include:

1. **Prerequisites**: What's needed before this document
2. **Next Steps**: What to do after this document
3. **Related Topics**: Connected concepts or procedures

### **Cross-Reference Principles**

1. **Rich Interconnections**: Every document should link to at least 3-5 related documents
2. **Contextual Links**: Explain WHY each link is relevant
3. **Bidirectional Linking**: When A links to B, B should also link back to A
4. **Learning Paths**: Create logical sequences through related documents
5. **Alternative Routes**: Provide multiple navigation paths for different use cases

### **Link Formatting**

```markdown
### **Prerequisites**

- [Required Topic](./path/to/topic.md) - Brief explanation of why it's required

### **Next Steps**

- [Follow-up Topic](./path/to/next.md) - What this enables you to do

### **Related Topics**

- [Related Concept](./path/to/related.md) - How it connects to current topic
```

### **Navigation Breadcrumbs**

Every document MUST include navigation context:

```markdown
## 🧭 **Navigation Context**

**🏠 Root**: [Home](../index.md) → **📂 Hub**: [Section](./index.md) → **📄 Current**: Document Name
```

### **Date Tracking (MANDATORY)**

All reorganized documents MUST include the reorganization date:

```markdown
**Updated**: 2025-06-11
```

This date must appear in the footer metadata line alongside Framework version.

---

## 📊 **Code Documentation Standards**

### **API Documentation**

- **Validate Against Code**: All API docs must reflect actual implementation in `/flext/src/`
- **Complete Examples**: Every API includes working code examples
- **Error Cases**: Document common error scenarios and solutions
- **Type Information**: Include complete type information for Python 3.13+

### **Code Examples**

```python
# Good: Complete, runnable example
from flext.core import Entity
from datetime import datetime, UTC

class Customer(Entity):
    """Customer entity with proper domain logic.

    Example:
        >>> customer = Customer(
        ...     name="John Doe",
        ...     email="john@example.com"
        ... )
        >>> customer.activate()
        >>> assert customer.is_active
    """
    def activate(self) -> None:
        """Activate customer account."""
        self.is_active = True
        self.activated_at = datetime.now(UTC)
```

### **Docstring Standards**

Follow **PEP 8 + Google Style**:

```python
def process_order(order_id: str, priority: bool = False) -> OrderResult:
    """Process an order with optional priority handling.

    Args:
        order_id: Unique identifier for the order
        priority: Whether to process with high priority

    Returns:
        OrderResult with processing status and details

    Raises:
        OrderNotFound: When order_id doesn't exist
        ProcessingError: When order processing fails

    Example:
        >>> result = process_order("ORD-123", priority=True)
        >>> assert result.status == "completed"
    """
```

---

## 🚨 **Compliance Requirements**

### **Mandatory Elements**

Every document MUST include:

1. **📂 Navigation Context**: Breadcrumb navigation
2. **🎯 Quick Links**: Section hub and root links
3. **🔗 Cross-References**: Prerequisites, next steps, related topics
4. **📊 Hub Reference**: Link back to section hub
5. **🏠 Root Reference**: Link to documentation root

### **Template Compliance**

- **Hub Documents**: MUST use hub template exactly
- **Content Documents**: MUST use document template exactly
- **Cross-References**: MUST include all three types (prerequisites, next steps, related)
- **Navigation**: MUST provide clear navigation context

### **Quality Gates**

Before publishing any documentation:

1. **✅ Template Compliance**: Follows mandatory templates
2. **✅ Navigation Working**: All links functional
3. **✅ Cross-References Complete**: All reference types included
4. **✅ Code Validation**: API docs match actual code
5. **✅ English Language**: No Portuguese or other languages
6. **✅ Current Content**: No obsolete or future-dated content

---

## 🔧 **Tools & Automation**

### **Validation Tools**

- **Link Checker**: Automated validation of all internal links
- **Template Checker**: Validation against mandatory templates
- **Code Sync**: Verification that API docs match `/flext/src/` code
- **Language Check**: Automated detection of non-English content

### **Maintenance Workflow**

1. **Content Creation**: Follow templates and standards
2. **Peer Review**: Cross-validation by other contributors
3. **Code Validation**: Verify against actual implementation
4. **Link Testing**: Ensure all navigation works
5. **Publication**: Update with proper metadata

---

## 👥 **Agent Coordination Guidelines**

### **For Documentation Agents**

When working on documentation:

1. **🚨 MANDATORY**: Follow `/docs/index.md` as absolute root
2. **🚨 MANDATORY**: Apply unified templates to ALL documents
3. **🚨 MANDATORY**: Implement hierarchical navigation
4. **🚨 MANDATORY**: Add cross-references to every document

### **Coordination Protocol**

- **Token Updates**: Report template compliance in coordination token
- **Cross-Agent Review**: Validate each other's template application
- **Conflict Resolution**: Escalate template violations to AGENT_ZERO
- **Quality Assurance**: Cross-check navigation and links

### **Deliverables**

Each agent must deliver:

- **Template Compliance Report**: Verification of template application
- **Navigation Validation**: Confirmation of hierarchical structure
- **Cross-Reference Audit**: Complete cross-reference implementation
- **Quality Metrics**: Coverage and compliance statistics

---

## 📈 **Metrics & Quality Assurance**

### **Documentation Metrics**

- **Template Compliance**: 100% required
- **Navigation Coverage**: All documents linked hierarchically
- **Cross-Reference Density**: Minimum 90% coverage
- **Code Validation**: 100% API accuracy
- **Link Health**: 0% broken links

### **Quality Review Process**

1. **Template Validation**: Automated template compliance check
2. **Content Review**: Manual review for quality and accuracy
3. **Navigation Testing**: Automated link and navigation validation
4. **Code Sync**: Verification against actual implementation
5. **Final Approval**: AGENT_ZERO validation and sign-off

---

## 🆘 **Common Issues & Solutions**

### **Template Violations**

**Issue**: Document doesn't follow mandatory template
**Solution**: Apply correct template from this guide
**Prevention**: Use templates as starting point for all new documents

### **Broken Navigation**

**Issue**: Links to non-existent files or incorrect paths
**Solution**: Verify all paths relative to document location
**Prevention**: Test all links before publishing

### **Missing Cross-References**

**Issue**: Document lacks prerequisites, next steps, or related topics
**Solution**: Add all three mandatory cross-reference types
**Prevention**: Use template checklist for every document

### **Code Validation Failures**

**Issue**: API documentation doesn't match actual code
**Solution**: Review `/flext/src/` code and update documentation
**Prevention**: Regular sync validation between docs and code

---

## 🎯 **Quick Reference Checklist**

### **For Every Document**

- [ ] Uses correct template (hub or content)
- [ ] Includes navigation context breadcrumb
- [ ] Has all three cross-reference types
- [ ] Links back to section hub and documentation root
- [ ] Content is current and validated
- [ ] Language is English only
- [ ] Code examples are complete and runnable
- [ ] Includes date 2025-06-11 in footer metadata
- [ ] Has at least 3-5 cross-reference links to related documents

### **For Hub Documents**

- [ ] Uses hub template exactly
- [ ] Includes topic navigation table
- [ ] Has learning path progression
- [ ] Provides cross-section navigation
- [ ] Lists section metrics

### **For API Documentation**

- [ ] Validated against actual `/flext/src/` code
- [ ] Complete type information
- [ ] Working code examples
- [ ] Error case documentation
- [ ] Proper docstring format (PEP8 + Google)

---

## 🔗 **Cross-References**

### **Prerequisites**

- [Documentation Root Index](./index.md) - Understanding the overall structure
- [Mandatory Compliance Directive](./MANDATORY_COMPLIANCE_DIRECTIVE.md) - Required standards

### **Next Steps**

- [Architecture Documentation](./architecture/index.md) - Apply standards to architecture docs
- [Development Documentation](./development/index.md) - Apply standards to development docs
- [Guides Documentation](./guides/index.md) - Apply standards to practical guides

### **Related Topics**

- [Standardization Master Plan](./STANDARDIZATION_MASTER_PLAN.md) - Overall coordination strategy
- [Agent Coordination](/.doc_migration_coordination.json) - Multi-agent coordination system

---

**📂 Hub**: [Documentation Root](./index.md) | **🏠 Root**: [Documentation Home](./index.md) | **Framework**: FLEXT 0.4.0+ | **Updated**: 2025-06-11
