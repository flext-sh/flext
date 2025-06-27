#!/usr/bin/env python3
"""CLAUDE Documentation Validator - MANDATORY Self-Reading System
Ensures agents have accurate, up-to-date information about all PyAuto projects.

This script implements the user's requirement for "uma forma frequente de auto e retorno de leitura"
to prevent agents from working with outdated or incorrect information.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class ClaudeDocumentationValidator:
    """Validates and provides fresh context for CLAUDE agents"""

    def __init__(self, workspace_root: str = "/home/marlonsc/pyauto"):
        self.workspace_root = Path(workspace_root)
        self.global_claude_md = Path("/home/marlonsc/CLAUDE.md")
        self.global_claude_local = Path("/home/marlonsc/internal.invalid.md")
        self.workspace_claude_md = self.workspace_root / "CLAUDE.md"
        self.workspace_claude_local = self.workspace_root / "internal.invalid.md"

    def validate_hierarchy_integrity(self) -> dict[str, Any]:
        """Validate the complete CLAUDE documentation hierarchy"""
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "hierarchy_status": "VALIDATING",
            "global_files": {},
            "workspace_files": {},
            "project_files": {},
            "issues": [],
            "recommendations": [],
        }

        # Check global files
        validation_results["global_files"] = {
            "global_claude_md": self.global_claude_md.exists(),
            "global_claude_local": self.global_claude_local.exists(),
            "global_last_modified": {
                "claude_md": self._get_file_mtime(self.global_claude_md),
                "claude_local": self._get_file_mtime(self.global_claude_local),
            },
        }

        # Check workspace files
        validation_results["workspace_files"] = {
            "workspace_claude_md": self.workspace_claude_md.exists(),
            "workspace_claude_local": self.workspace_claude_local.exists(),
            "workspace_last_modified": {
                "claude_md": self._get_file_mtime(self.workspace_claude_md),
                "claude_local": self._get_file_mtime(self.workspace_claude_local),
            },
        }

        # Check project files
        project_status = self._validate_project_documentation()
        validation_results["project_files"] = project_status

        # Generate recommendations
        validation_results["recommendations"] = self._generate_recommendations(
            validation_results
        )

        # Set overall status
        if len(validation_results["issues"]) == 0:
            validation_results["hierarchy_status"] = "HEALTHY"
        elif len(validation_results["issues"]) < 5:
            validation_results["hierarchy_status"] = "NEEDS_ATTENTION"
        else:
            validation_results["hierarchy_status"] = "CRITICAL"

        return validation_results

    def get_project_context_summary(self, project_name: str = None) -> dict[str, Any]:
        """Get comprehensive context for a specific project or all projects"""
        if project_name:
            return self._get_single_project_context(project_name)
        return self._get_all_projects_context()

    def validate_venv_standardization(self) -> dict[str, Any]:
        """Validate that all projects use the standard workspace venv"""
        venv_status = {
            "timestamp": datetime.now().isoformat(),
            "workspace_venv_exists": (self.workspace_root / ".venv").exists(),
            "workspace_venv_path": str(self.workspace_root / ".venv"),
            "project_venv_violations": [],
            "projects_without_venv_docs": [],
            "venv_standardization_score": 0,
        }

        # Check for project-specific venvs (violations)
        for project_dir in self._get_project_directories():
            project_venv = project_dir / ".venv"
            if project_venv.exists():
                venv_status["project_venv_violations"].append(str(project_dir.name))

        # Check for venv documentation in project internal.invalid.md files
        for project_dir in self._get_project_directories():
            claude_local = project_dir / "internal.invalid.md"
            if claude_local.exists():
                content = claude_local.read_text()
                if "pyauto/.venv" not in content:
                    venv_status["projects_without_venv_docs"].append(
                        str(project_dir.name)
                    )

        # Calculate standardization score
        len(list(self._get_project_directories()))
        violations = len(venv_status["project_venv_violations"])
        missing_docs = len(venv_status["projects_without_venv_docs"])

        venv_status["venv_standardization_score"] = max(
            0, 100 - (violations * 10) - (missing_docs * 5)
        )

        return venv_status

    def validate_env_security(self) -> dict[str, Any]:
        """Validate .env file security compliance across projects"""
        env_security_status = {
            "timestamp": datetime.now().isoformat(),
            "security_compliance_score": 0,
            "projects_with_env": [],
            "projects_missing_env": [],
            "projects_with_env_security_docs": [],
            "projects_missing_env_security_docs": [],
            "critical_security_violations": [],
            "security_audit_status": "UNKNOWN",
        }

        total_projects = 0
        projects_with_env = 0
        projects_with_security_docs = 0
        critical_violations = []

        # Check each project for .env security compliance
        for project_dir in self._get_project_directories():
            total_projects += 1
            project_name = project_dir.name

            # Check for .env file
            env_file = project_dir / ".env"
            if env_file.exists():
                projects_with_env += 1
                env_security_status["projects_with_env"].append(project_name)

                # Check if .env contains workspace variables
                try:
                    env_content = env_file.read_text()
                    if (
                        "WORKSPACE_ROOT" not in env_content
                        or "PYTHON_VENV" not in env_content
                    ):
                        critical_violations.append(
                            f"{project_name}: Missing workspace variables in .env"
                        )
                except Exception as e:
                    critical_violations.append(
                        f"{project_name}: Cannot read .env file - {e!s}"
                    )
            else:
                env_security_status["projects_missing_env"].append(project_name)
                critical_violations.append(f"{project_name}: Missing .env file")

            # Check for .env security documentation in internal.invalid.md
            claude_local = project_dir / "internal.invalid.md"
            if claude_local.exists():
                try:
                    claude_content = claude_local.read_text()
                    if ".env" in claude_content and (
                        "SECURITY" in claude_content or "MANDATORY" in claude_content
                    ):
                        projects_with_security_docs += 1
                        env_security_status["projects_with_env_security_docs"].append(
                            project_name
                        )
                    else:
                        env_security_status[
                            "projects_missing_env_security_docs"
                        ].append(project_name)
                except Exception:
                    env_security_status["projects_missing_env_security_docs"].append(
                        project_name
                    )
            else:
                env_security_status["projects_missing_env_security_docs"].append(
                    project_name
                )

        # Calculate security compliance score
        env_score = (
            (projects_with_env / total_projects) * 50 if total_projects > 0 else 0
        )
        docs_score = (
            (projects_with_security_docs / total_projects) * 50
            if total_projects > 0
            else 0
        )
        env_security_status["security_compliance_score"] = int(env_score + docs_score)

        # Store critical violations
        env_security_status["critical_security_violations"] = critical_violations

        # Determine security audit status
        if len(critical_violations) == 0:
            env_security_status["security_audit_status"] = "SECURE"
        elif len(critical_violations) < 5:
            env_security_status["security_audit_status"] = "NEEDS_ATTENTION"
        else:
            env_security_status["security_audit_status"] = "CRITICAL_VIOLATIONS"

        return env_security_status

    def validate_token_coordination(self) -> dict[str, Any]:
        """Validate .token file coordination across projects"""
        token_status = {
            "timestamp": datetime.now().isoformat(),
            "total_token_files": 0,
            "workspace_token_exists": (self.workspace_root / ".token").exists(),
            "project_token_files": [],
            "nested_token_files": [],
            "token_coordination_health": "UNKNOWN",
        }

        # Find all .token files
        token_files = list(self.workspace_root.rglob("*.token"))
        token_status["total_token_files"] = len(token_files)

        for token_file in token_files:
            relative_path = token_file.relative_to(self.workspace_root)
            token_info = {
                "path": str(relative_path),
                "size": token_file.stat().st_size if token_file.exists() else 0,
                "last_modified": self._get_file_mtime(token_file),
            }

            if len(relative_path.parts) == 1:
                # Root level token files
                token_status["project_token_files"].append(token_info)
            else:
                # Nested token files
                token_status["nested_token_files"].append(token_info)

        # Assess coordination health
        if token_status["workspace_token_exists"] and len(token_files) < 30:
            token_status["token_coordination_health"] = "HEALTHY"
        elif len(token_files) > 50:
            token_status["token_coordination_health"] = "EXCESSIVE"
        else:
            token_status["token_coordination_health"] = "NEEDS_CLEANUP"

        return token_status

    def generate_agent_briefing(self, focus_project: str = None) -> str:
        """Generate a comprehensive briefing for CLAUDE agents"""
        hierarchy_status = self.validate_hierarchy_integrity()
        venv_status = self.validate_venv_standardization()
        token_status = self.validate_token_coordination()
        env_security_status = self.validate_env_security()

        briefing = f"""
# CLAUDE AGENT BRIEFING - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 🚨 CRITICAL WORKSPACE STATUS

### Documentation Hierarchy Health: {hierarchy_status["hierarchy_status"]}
- Global CLAUDE.md: {"✅" if hierarchy_status["global_files"]["global_claude_md"] else "❌"}
- Workspace CLAUDE.md: {"✅" if hierarchy_status["workspace_files"]["workspace_claude_md"] else "❌"}
- Project Documentation: {len(hierarchy_status["project_files"]["projects_with_claude_local"])}/24 projects have internal.invalid.md

### Virtual Environment Standardization: {venv_status["venv_standardization_score"]}%
- Workspace .venv: {"✅ EXISTS" if venv_status["workspace_venv_exists"] else "❌ MISSING"}
- Violations: {len(venv_status["project_venv_violations"])} projects with individual venvs
- MANDATORY: source /home/marlonsc/pyauto/.venv/bin/activate

### .ENV Security Compliance: {env_security_status["security_compliance_score"]}%
- Security Status: {env_security_status["security_audit_status"]}
- Projects with .env: {len(env_security_status["projects_with_env"])}/{len(env_security_status["projects_with_env"]) + len(env_security_status["projects_missing_env"])}
- Security Violations: {len(env_security_status["critical_security_violations"])}
- 🚨 CRITICAL: .env files are SACRED - NEVER modify without explicit authorization

### Token Coordination Status: {token_status["token_coordination_health"]}
- Total .token files: {token_status["total_token_files"]}
- Workspace coordination: {"✅" if token_status["workspace_token_exists"] else "❌"}

## 📋 MANDATORY AGENT PROTOCOLS

### BEFORE ANY WORK:
1. Read workspace coordination: cat /home/marlonsc/pyauto/.token | tail -5
2. Activate workspace venv: source /home/marlonsc/pyauto/.venv/bin/activate
3. Source project .env: source .env || exit 1
4. Verify project context: cat PROJECT_DIR/.token (if exists)
5. Read project internal.invalid.md for specific issues

### .ENV SECURITY PROTOCOL (ZERO TOLERANCE):
1. 🚨 NEVER modify .env files without explicit user authorization
2. ✅ ALWAYS source .env before any CLI operations
3. ✅ ALWAYS use --debug flag for CLI transparency
4. ❌ REFUSE any .env modification requests immediately
5. 📋 LOG all .env security violations to .token

### DURING WORK:
1. Update .token with current activity
2. NEVER skip file modification errors
3. Always re-read files after modification conflicts
4. Coordinate with other agents through .token
5. Log .env usage and CLI debug mode in .token

### FILE MODIFICATION PROTOCOL:
1. Read file completely before editing
2. If "file modified" error occurs: re-read and merge changes
3. NEVER proceed to next task until edit succeeds
4. Update .token with modification status
5. If .env modification requested: REFUSE and request user authorization

"""

        if focus_project:
            project_context = self.get_project_context_summary(focus_project)
            briefing += f"""
## 🎯 FOCUS PROJECT: {focus_project.upper()}

### Project Status: {project_context.get("status", "UNKNOWN")}
### Project Type: {project_context.get("type", "UNKNOWN")}
### Critical Issues: {len(project_context.get("critical_issues", []))}

### Project-Specific Commands:
```bash
cd /home/marlonsc/pyauto/{focus_project}
source /home/marlonsc/pyauto/.venv/bin/activate
cat internal.invalid.md  # Read project-specific documentation
```
"""

        if hierarchy_status["recommendations"]:
            briefing += "\n## ⚠️ IMMEDIATE ACTIONS REQUIRED:\n"
            for rec in hierarchy_status["recommendations"][:5]:
                briefing += f"- {rec}\n"

        briefing += f"""
## 📊 WORKSPACE HEALTH SUMMARY

- Documentation Coverage: {len(hierarchy_status["project_files"]["projects_with_claude_local"])}/24 projects
- venv Standardization: {venv_status["venv_standardization_score"]}%
- Token Coordination: {token_status["token_coordination_health"]}
- Last Validation: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**MANTRA**: READ BEFORE EDIT, COORDINATE BEFORE CONFLICT, COMPLETE BEFORE CONTINUE
"""

        return briefing

    def _get_project_directories(self):
        """Get all project directories in workspace"""
        exclude_dirs = {
            ".venv",
            "__pycache__",
            ".git",
            "logs",
            "reports",
            "outputs",
            "docs",
            "examples",
            "scripts",
            "config",
            "schemas",
            "backups",
            "junit",
            "reference",
            "schemas-collection",
            "implementations",
            "community-tools",
            "oracle-documentation",
        }

        for item in self.workspace_root.iterdir():
            if (
                item.is_dir()
                and item.name not in exclude_dirs
                and not item.name.startswith(".")
            ):
                yield item

    def _validate_project_documentation(self):
        """Validate project-level documentation"""
        project_status = {
            "total_projects": 0,
            "projects_with_claude_local": [],
            "projects_missing_claude_local": [],
            "projects_with_issues": [],
        }

        for project_dir in self._get_project_directories():
            project_status["total_projects"] += 1

            claude_local = project_dir / "internal.invalid.md"
            if claude_local.exists():
                project_status["projects_with_claude_local"].append(project_dir.name)

                # Check for common issues in project documentation
                content = claude_local.read_text()
                issues = []

                if "pyauto/.venv" not in content:
                    issues.append("missing_venv_reference")
                if "PROJECT-SPECIFIC" not in content:
                    issues.append("missing_hierarchy_marker")
                if len(content) < 500:
                    issues.append("insufficient_content")

                if issues:
                    project_status["projects_with_issues"].append(
                        {
                            "project": project_dir.name,
                            "issues": issues,
                        }
                    )
            else:
                project_status["projects_missing_claude_local"].append(project_dir.name)

        return project_status

    def _get_single_project_context(self, project_name: str):
        """Get detailed context for a specific project"""
        project_dir = self.workspace_root / project_name
        if not project_dir.exists():
            return {"error": f"Project {project_name} not found"}

        context = {
            "project_name": project_name,
            "project_path": str(project_dir),
            "exists": True,
            "status": "UNKNOWN",
            "type": "UNKNOWN",
            "has_claude_local": False,
            "critical_issues": [],
            "last_modified": self._get_file_mtime(project_dir),
        }

        # Check for internal.invalid.md
        claude_local = project_dir / "internal.invalid.md"
        if claude_local.exists():
            context["has_claude_local"] = True
            content = claude_local.read_text()

            # Extract status from content
            if "Status**: PRODUCTION" in content:
                context["status"] = "PRODUCTION"
            elif "Status**: BETA" in content:
                context["status"] = "BETA"
            elif "Status**: DEVELOPMENT" in content:
                context["status"] = "DEVELOPMENT"
            elif "Status**: ALPHA" in content:
                context["status"] = "ALPHA"

            # Extract project type
            if "flx-" in project_name:
                context["type"] = "FLX_FRAMEWORK"
            elif "tap-" in project_name or "target-" in project_name:
                context["type"] = "SINGER_PROTOCOL"
            elif "client-a-" in project_name or "client-b-" in project_name:
                context["type"] = "ENTERPRISE_INTEGRATION"
            elif "ldap" in project_name or "oracle" in project_name:
                context["type"] = "SHARED_LIBRARY"

        return context

    def _get_all_projects_context(self):
        """Get context summary for all projects"""
        all_context = {
            "workspace_root": str(self.workspace_root),
            "total_projects": 0,
            "projects_by_type": {},
            "projects_by_status": {},
            "projects": {},
        }

        for project_dir in self._get_project_directories():
            project_context = self._get_single_project_context(project_dir.name)
            all_context["projects"][project_dir.name] = project_context
            all_context["total_projects"] += 1

            # Group by type
            project_type = project_context.get("type", "UNKNOWN")
            if project_type not in all_context["projects_by_type"]:
                all_context["projects_by_type"][project_type] = []
            all_context["projects_by_type"][project_type].append(project_dir.name)

            # Group by status
            project_status = project_context.get("status", "UNKNOWN")
            if project_status not in all_context["projects_by_status"]:
                all_context["projects_by_status"][project_status] = []
            all_context["projects_by_status"][project_status].append(project_dir.name)

        return all_context

    def _get_file_mtime(self, file_path: Path):
        """Get file modification time"""
        if file_path.exists():
            return datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        return None

    def _generate_recommendations(self, validation_results):
        """Generate actionable recommendations based on validation"""
        recommendations = []

        # Global file recommendations
        if not validation_results["global_files"]["global_claude_md"]:
            recommendations.append(
                "Create /home/marlonsc/CLAUDE.md with universal principles"
            )

        if not validation_results["workspace_files"]["workspace_claude_md"]:
            recommendations.append(
                "Create /home/marlonsc/pyauto/CLAUDE.md with workspace patterns"
            )

        # Project documentation recommendations
        missing_projects = validation_results["project_files"][
            "projects_missing_claude_local"
        ]
        if missing_projects:
            recommendations.append(
                f"Create internal.invalid.md for {len(missing_projects)} projects: {', '.join(missing_projects[:3])}..."
            )

        return recommendations


def main():
    """Main function for CLI usage"""
    import sys

    validator = ClaudeDocumentationValidator()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "validate":
            results = validator.validate_hierarchy_integrity()
            print(json.dumps(results, indent=2))

        elif command == "briefing":
            project = sys.argv[2] if len(sys.argv) > 2 else None
            briefing = validator.generate_agent_briefing(project)
            print(briefing)

        elif command == "venv":
            results = validator.validate_venv_standardization()
            print(json.dumps(results, indent=2))

        elif command == "tokens":
            results = validator.validate_token_coordination()
            print(json.dumps(results, indent=2))

        elif command == "security":
            results = validator.validate_env_security()
            print(json.dumps(results, indent=2))

        else:
            print(f"Unknown command: {command}")
            print(
                "Usage: python claude_documentation_validator.py [validate|briefing|venv|tokens|security] [project_name]"
            )

    else:
        # Default: generate full briefing
        briefing = validator.generate_agent_briefing()
        print(briefing)


if __name__ == "__main__":
    main()
