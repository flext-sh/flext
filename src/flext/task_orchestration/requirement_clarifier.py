"""Requirement Clarifier Component for FLEXT Task Orchestration.

Extracted from FlextTaskOrchestration service to handle requirement analysis,
parsing, filtering, validation, and clarification question generation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

from flext_core import FlextCore

from .constants import FlextTaskOrchestrationConstants


class RequirementClarifier:
    """Handles requirement clarification, parsing, and validation.

    This component is responsible for:
    - Extracting requirements from text input
    - Applying focus area filtering
    - Validating requirement completeness
    - Generating clarification questions
    """

    def __init__(self, logger: FlextCore.Logger, focus_area: str | None = None) -> None:
        """Initialize the requirement clarifier.

        Args:
            logger: Logger instance for operation tracking
            focus_area: Optional focus area for requirement filtering

        """
        super().__init__()
        self._logger = logger
        self._focus_area = focus_area

    def clarify_requirements(
        self, input_data: str | Path, context: dict[str, object] | None = None
    ) -> FlextCore.Result[dict[str, object]]:
        """Clarify and extract requirements from input.

        Args:
            input_data: Text content or file path containing requirements
            context: Optional context information

        Returns:
            FlextCore.Result containing clarified requirements with questions

        """
        try:
            self._logger.info("Starting requirement clarification process")

            # Extract text content
            if isinstance(input_data, Path):
                if not input_data.exists():
                    return FlextCore.Result[dict[str, object]].fail(
                        FlextTaskOrchestrationConstants.Messages.FILE_NOT_FOUND.format(
                            path=input_data
                        )
                    )
                content = input_data.read_text(encoding="utf-8")
            else:
                content = str(input_data)

            # Parse requirements
            requirements = self._parse_requirements(content)

            # Apply focus filtering if configured
            if self._focus_area:
                requirements = self._filter_by_focus(requirements, self._focus_area)

            # Validate requirements
            validation_result = self._validate_requirements(requirements)
            if validation_result.is_failure:
                return validation_result

            # Generate clarification questions
            questions = self._generate_clarification_questions(requirements)

            result = {
                "requirements": requirements,
                "questions": questions,
                "context": context or {},
                "focus_area": self._focus_area,
                "extracted_at": datetime.now(UTC).isoformat(),
            }

            self._logger.info(
                FlextTaskOrchestrationConstants.Messages.REQUIREMENTS_CLARIFIED.format(
                    count=len(requirements)
                )
            )
            return FlextCore.Result[dict[str, object]].ok(result)

        except Exception as e:
            error = FlextTaskOrchestrationConstants.Messages.REQUIREMENT_CLARIFICATION_FAILED.format(
                error=str(e)
            )
            self._logger.exception(error)
            return FlextCore.Result[dict[str, object]].fail(error)

    def _parse_requirements(self, content: str) -> list[dict[str, object]]:
        """Parse requirements from text content using constants.

        Args:
            content: Text content to parse

        Returns:
            List of parsed requirement dictionaries

        """
        requirements = []
        lines = content.split("\n")
        current_requirement = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for numbered lists
            numbered_match = re.match(
                FlextTaskOrchestrationConstants.TaskPatterns.NUMBERED_LIST, line
            )
            if numbered_match:
                if current_requirement:
                    requirements.append(current_requirement)

                current_requirement = {
                    "id": numbered_match.group(1),
                    "title": numbered_match.group(2),
                    "description": "",
                    "priority": FlextTaskOrchestrationConstants.TaskPriority.MEDIUM,
                    "type": FlextTaskOrchestrationConstants.TaskType.FEATURE,
                }
                continue

            # Check for bullet points
            bullet_match = re.match(
                FlextTaskOrchestrationConstants.TaskPatterns.BULLET_POINT, line
            )
            if bullet_match:
                if current_requirement:
                    requirements.append(current_requirement)

                current_requirement = {
                    "id": f"req_{len(requirements) + 1}",
                    "title": bullet_match.group(1),
                    "description": "",
                    "priority": FlextTaskOrchestrationConstants.TaskPriority.MEDIUM,
                    "type": FlextTaskOrchestrationConstants.TaskType.FEATURE,
                }
                continue

            # Accumulate description for current requirement
            if current_requirement:
                if current_requirement["description"]:
                    current_requirement["description"] += " "
                current_requirement["description"] += line

        # Add the last requirement
        if current_requirement:
            requirements.append(current_requirement)

        return requirements

    def _filter_by_focus(
        self, requirements: list[dict[str, object]], focus_area: str
    ) -> list[dict[str, object]]:
        """Filter requirements by focus area.

        Args:
            requirements: List of requirements to filter
            focus_area: Focus area string to match against

        Returns:
            Filtered list of requirements

        """
        focus_lower = focus_area.lower()
        filtered = []

        for req in requirements:
            title_lower = req.get("title", "").lower()
            desc_lower = req.get("description", "").lower()

            if (
                focus_lower in title_lower
                or focus_lower in desc_lower
                or any(tag.lower() == focus_lower for tag in req.get("tags", []))
            ):
                filtered.append(req)

        return filtered

    def _validate_requirements(
        self, requirements: list[dict[str, object]]
    ) -> FlextCore.Result[dict[str, object]]:
        """Validate extracted requirements.

        Args:
            requirements: List of requirements to validate

        Returns:
            Validation result

        """
        if not requirements:
            return FlextCore.Result[dict[str, object]].fail(
                FlextTaskOrchestrationConstants.Messages.NO_REQUIREMENTS_EXTRACTED
            )

        # Check for minimum requirements
        if len(requirements) < 1:
            return FlextCore.Result[dict[str, object]].fail(
                FlextTaskOrchestrationConstants.Messages.AT_LEAST_ONE_REQUIREMENT_NEEDED
            )

        # Validate each requirement
        for i, req in enumerate(requirements):
            if not req.get("title", "").strip():
                return FlextCore.Result[dict[str, object]].fail(
                    FlextTaskOrchestrationConstants.Messages.REQUIREMENT_MISSING_TITLE.format(
                        index=i + 1
                    )
                )

        return FlextCore.Result[dict[str, object]].ok({
            "validated": True,
            "count": len(requirements),
        })

    def _generate_clarification_questions(
        self, requirements: list[dict[str, object]]
    ) -> FlextCore.Types.StringList:
        """Generate clarification questions for requirements.

        Args:
            requirements: List of requirements to analyze

        Returns:
            List of clarification questions

        """
        questions = []

        # Check for vague requirements
        vague_indicators = ["improve", "better", "fix", "optimize", "enhance"]
        for req in requirements:
            title = req.get("title", "").lower()
            if any(indicator in title for indicator in vague_indicators):
                questions.append(
                    f"Can you provide more specific details for '{req.get('title')}'?"
                )

        # Check for missing priorities
        if not any(
            req.get("priority") != FlextTaskOrchestrationConstants.TaskPriority.MEDIUM
            for req in requirements
        ):
            questions.append("Are there any high-priority or critical requirements?")

        # Check for missing context
        if not any(req.get("description") for req in requirements):
            questions.append(
                "Would you like to add more detailed descriptions to any requirements?"
            )

        return questions
