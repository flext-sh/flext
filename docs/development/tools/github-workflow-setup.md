# ⚙️ GitHub Workflow Setup Guide

> **Function**: CI/CD pipeline configuration and GitHub workflow automation | **Audience**: DevOps engineers, developers | **Status**: Production-Ready

[![GitHub](https://img.shields.io/badge/GitHub-workflows-black.svg)](./index.md)
[![CI/CD](https://img.shields.io/badge/CI_CD-automated-green.svg)](../standards/index.md)
[![Framework](https://img.shields.io/badge/framework-FLX%200.4.0-orange.svg)](../../index.md)

**Complete GitHub workflow setup guide for FLX Framework including CI/CD pipeline configuration, automated testing, and deployment workflows - validated against production implementations**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Development](../index.md) → **📂 Section**: [Tools](./index.md) → **📄 Current**: GitHub Workflow Setup

This guide addresses OAuth scope restrictions when pushing GitHub workflow files. GitHub restricts workflow file updates for security reasons. Here's how to add them properly:

## Option 1: Use the GitHub Web Interface (Recommended)

1. Go to [your repository](https://github.com/datacosmos-br/dc-api-x)
2. Navigate to the `.github/workflows` directory
3. For each workflow file:
   - Click "Add file" → "Create new file"
   - Name the file (e.g., `docs.yml`)
   - Copy and paste the content from the corresponding file in the `/home/marlonsc/pyauto/temp_workflows/` directory
   - Commit directly to the main branch

## Option 2: Use a Personal Access Token with Workflow Scope

1. Go to [GitHub Personal Access Token settings](https://github.com/settings/tokens)
2. Create a new token with `workflow` scope (and other needed scopes)
3. Use this token for git authentication:

   ```bash
   git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/datacosmos-br/dc-api-x.git
   git checkout main
   git push origin main
   ```

## Option 3: Create a Pull Request from the Web Interface

1. Go to [your repository](https://github.com/datacosmos-br/dc-api-x)
2. Click on "Pull requests" tab
3. Click "New pull request"
4. Set the base branch to `main` and compare branch to `config-without-workflows`
5. Create the pull request
6. After merging, add workflow files using the GitHub web interface

## Workflow Files

I've saved all your workflow files in:

- The `/home/marlonsc/pyauto/temp_workflows/` directory (individual files)
- The `/home/marlonsc/pyauto/github_workflows.zip` file (zip archive)

## Which Files to Add

Add these workflow files:

1. `docs.yml` - Documentation build and deployment
2. `greetings.yml` - Welcome messages for contributors
3. `label.yml` - Automatic PR labeling
4. `python-workflow.yml` - Main CI/CD pipeline
5. `release.yml` - Release automation
6. `security-scans.yml` - Security scanning
7. `stale.yml` - Stale issue management
8. `summary.yml` - Issue summarization

---

## 🔗 **Cross-References**

### **⬅️ Essential Prerequisites**

- [**Development Standards Foundation**](../standards/python-modernization-guide.md) - Code quality standards and development practices required for CI/CD configuration
- [**Testing Framework Setup**](../testing/testing-framework.md) - Testing infrastructure required for automated CI/CD pipeline validation
- [**Development Tools Hub**](./index.md) - Development tools overview and automation framework understanding

### **➡️ Implementation Next Steps**

- [**Testing Integration**](../testing/hexagonal-testing-guide.md) - Testing strategies for CI/CD pipeline validation and automated quality gates
- [**Deployment Automation**](../../deployment/kubernetes-deployment.md) - Production deployment strategies utilizing GitHub workflow automation
- [**Performance Monitoring Integration**](../../infrastructure/operational-excellence.md) - Monitoring and observability integration with CI/CD pipelines

### **🔗 Related Implementation Topics**

- [**Development Standards Documentation**](../standards/documentation-standards.md) - Documentation standards enforced through GitHub workflow automation
- [**Security Implementation**](../../security/architecture/security-architecture.md) - Security scanning and validation in CI/CD pipelines
- [**API Reference for Automation**](../../api-reference/core-api-reference.md) - API documentation for components validated through automated workflows
- [**Oracle Integration Testing**](../../guides/oracle/oracle-integration-comprehensive-guide.md) - Oracle integration testing within CI/CD pipeline context
- [**Real-World Automation Examples**](../../examples/real-world-implementations.md) - Production CI/CD examples and workflow automation patterns
- [**Optimization Pipeline Integration**](../../optimization/performance/optimization-guide.md) - Performance optimization testing and validation in automated workflows

---

**📂 Content Document** | **🏠 Parent**: [Development Tools Hub](./index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
