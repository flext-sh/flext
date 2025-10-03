"""FLEXT CLI Prompts Tests - Comprehensive coverage.

Tests all functionality in FlextCliPrompts including user interactions,
status printing, and progress tracking.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from unittest.mock import patch

from flext_cli.prompts import FlextCliPrompts

from flext_core import FlextLogger, FlextTypes


class TestFlextCliPromptsInitialization:
    """Test FlextCliPrompts initialization and basic functionality."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        prompts = FlextCliPrompts()
        assert prompts._quiet is False
        assert prompts._logger is not None

    def test_init_with_logger(self) -> None:
        """Test initialization with custom logger."""
        logger = FlextLogger("test")
        prompts = FlextCliPrompts(logger=logger)
        assert prompts._logger is logger
        assert prompts._quiet is False

    def test_init_quiet_mode(self) -> None:
        """Test initialization in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        assert prompts._quiet is True

    def test_execute(self) -> None:
        """Test execute method returns success."""
        prompts = FlextCliPrompts()
        result = prompts.execute()
        assert result.is_success
        assert result.data is None


class TestFlextCliPromptsConfirm:
    """Test confirmation functionality."""

    def test_confirm_quiet_mode_default_true(self) -> None:
        """Test confirm in quiet mode with default True."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.confirm("Test message", default=True)
        assert result.is_success
        assert result.data is True

    def test_confirm_quiet_mode_default_false(self) -> None:
        """Test confirm in quiet mode with default False."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.confirm("Test message", default=False)
        assert result.is_success
        assert result.data is False

    @patch("builtins.input")
    def test_confirm_yes_response(self, mock_input: object) -> None:
        """Test confirm with yes response."""
        mock_input.return_value = "y"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is True

    @patch("builtins.input")
    def test_confirm_capitalized_yes(self, mock_input: object) -> None:
        """Test confirm with capitalized yes response."""
        mock_input.return_value = "YES"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is True

    @patch("builtins.input")
    def test_confirm_no_response(self, mock_input: object) -> None:
        """Test confirm with no response."""
        mock_input.return_value = "n"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_success
        assert result.data is False

    @patch("builtins.input")
    def test_confirm_empty_default_false(self, mock_input: object) -> None:
        """Test confirm with empty response and default False."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message", default=False)
        assert result.is_success
        assert result.data is False

    @patch("builtins.input")
    def test_confirm_empty_default_true(self, mock_input: object) -> None:
        """Test confirm with empty response and default True."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message", default=True)
        assert result.is_success
        assert result.data is True

    @patch("builtins.input")
    def test_confirm_invalid_response(self, mock_input: object) -> None:
        """Test confirm with invalid response."""
        mock_input.return_value = "maybe"
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message", default=False)
        assert result.is_success
        assert result.data is False  # Should use default

    @patch("builtins.input")
    def test_confirm_keyboard_interrupt(self, mock_input: object) -> None:
        """Test confirm with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_failure
        assert (
            result.error is not None and "User interrupted confirmation" in result.error
        )

    @patch("builtins.input")
    def test_confirm_eof_error(self, mock_input: object) -> None:
        """Test confirm with EOF error."""
        mock_input.side_effect = EOFError()
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_failure
        assert result.error is not None and "Input stream ended" in result.error

    @patch("builtins.input")
    def test_confirm_general_exception(self, mock_input: object) -> None:
        """Test confirm with general exception."""
        mock_input.side_effect = Exception("Test error")
        prompts = FlextCliPrompts()
        result = prompts.confirm("Test message")
        assert result.is_failure
        assert (
            result.error is not None
            and "Confirmation failed: Test error" in result.error
        )


class TestFlextCliPromptsPrompt:
    """Test prompt functionality."""

    def test_prompt_quiet_mode_with_default(self) -> None:
        """Test prompt in quiet mode with default value."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.prompt("Test message", default="default_value")
        assert result.is_success
        assert result.data == "default_value"

    def test_prompt_quiet_mode_no_default(self) -> None:
        """Test prompt in quiet mode without default should fail."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert result.error is not None and "Empty input is not allowed" in result.error

    @patch("builtins.input")
    def test_prompt_valid_input(self, mock_input: object) -> None:
        """Test prompt with valid input."""
        mock_input.return_value = "user_input"
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_success
        assert result.data == "user_input"

    @patch("builtins.input")
    def test_prompt_empty_with_default(self, mock_input: object) -> None:
        """Test prompt with empty input and default."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message", default="default_value")
        assert result.is_success
        assert result.data == "default_value"

    @patch("builtins.input")
    def test_prompt_empty_no_default(self, mock_input: object) -> None:
        """Test prompt with empty input and no default."""
        mock_input.return_value = ""
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert result.error is not None and "Empty input is not allowed" in result.error

    @patch("builtins.input")
    def test_prompt_whitespace_only(self, mock_input: object) -> None:
        """Test prompt with whitespace-only input."""
        mock_input.return_value = "   "
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert result.error is not None and "Empty input is not allowed" in result.error

    @patch("builtins.input")
    def test_prompt_keyboard_interrupt(self, mock_input: object) -> None:
        """Test prompt with keyboard interrupt."""
        mock_input.side_effect = KeyboardInterrupt()
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert result.error is not None and "User interrupted prompt" in result.error

    @patch("builtins.input")
    def test_prompt_eof_error(self, mock_input: object) -> None:
        """Test prompt with EOF error."""
        mock_input.side_effect = EOFError()
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert result.error is not None and "Input stream ended" in result.error

    @patch("builtins.input")
    def test_prompt_general_exception(self, mock_input: object) -> None:
        """Test prompt with general exception."""
        mock_input.side_effect = Exception("Test error")
        prompts = FlextCliPrompts()
        result = prompts.prompt("Test message")
        assert result.is_failure
        assert result.error is not None and "Prompt failed: Test error" in result.error


class TestFlextCliPromptsPrintStatus:
    """Test status printing functionality."""

    def test_print_status_info_quiet_mode(self) -> None:
        """Test print status info in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.print_status("Test message", status="info")
        assert result.is_success
        assert result.data is None

    def test_print_status_success_quiet_mode(self) -> None:
        """Test print status success in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.print_status("Test message", status="success")
        assert result.is_success
        assert result.data is None

    def test_print_status_warning_quiet_mode(self) -> None:
        """Test print status warning in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.print_status("Test message", status="warning")
        assert result.is_success
        assert result.data is None

    def test_print_status_error_quiet_mode(self) -> None:
        """Test print status error in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.print_status("Test message", status="error")
        assert result.is_success
        assert result.data is None

    def test_print_status_custom_status(self) -> None:
        """Test print status with custom status."""
        prompts = FlextCliPrompts()
        result = prompts.print_status("Test message", status="custom")
        assert result.is_success
        assert result.data is None

    def test_print_status_exception(self) -> None:
        """Test print status with exception."""
        prompts = FlextCliPrompts()
        # Mock logger to raise exception
        with patch.object(prompts._logger, "info", side_effect=Exception("Test error")):
            result = prompts.print_status("Test message", status="info")
            assert result.is_failure
            assert (
                result.error is not None
                and "Print status failed: Test error" in result.error
            )


class TestFlextCliPromptsConvenienceMethods:
    """Test convenience methods for status printing."""

    def test_print_success(self) -> None:
        """Test print success method."""
        prompts = FlextCliPrompts()
        result = prompts.print_success("Success message")
        assert result.is_success
        assert result.data is None

    def test_print_error(self) -> None:
        """Test print error method."""
        prompts = FlextCliPrompts()
        result = prompts.print_error("Error message")
        assert result.is_success
        assert result.data is None

    def test_print_warning(self) -> None:
        """Test print warning method."""
        prompts = FlextCliPrompts()
        result = prompts.print_warning("Warning message")
        assert result.is_success
        assert result.data is None

    def test_print_info(self) -> None:
        """Test print info method."""
        prompts = FlextCliPrompts()
        result = prompts.print_info("Info message")
        assert result.is_success
        assert result.data is None


class TestFlextCliPromptsProgress:
    """Test progress tracking functionality."""

    def test_create_progress_with_message_quiet_mode(self) -> None:
        """Test create progress with message in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        result = prompts.create_progress("Test progress")
        assert result.is_success
        assert result.data == "Test progress"

    def test_create_progress_with_message_normal_mode(self) -> None:
        """Test create progress with message in normal mode."""
        prompts = FlextCliPrompts()
        result = prompts.create_progress("Test progress")
        assert result.is_success
        assert result.data == "Test progress"

    def test_create_progress_empty_message(self) -> None:
        """Test create progress with empty message."""
        prompts = FlextCliPrompts()
        result = prompts.create_progress("")
        assert result.is_success
        assert not result.data

    def test_create_progress_exception(self) -> None:
        """Test create progress with exception."""
        prompts = FlextCliPrompts()
        # Mock logger to raise exception
        with patch.object(prompts._logger, "info", side_effect=Exception("Test error")):
            result = prompts.create_progress("Test progress")
            assert result.is_failure
            assert (
                result.error is not None
                and "Progress creation failed: Test error" in result.error
            )

    def test_with_progress_quiet_mode(self) -> None:
        """Test with progress in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)
        items = [1, 2, 3]
        result = prompts.with_progress(items, "Processing items")
        assert result.is_success
        assert result.data == items

    def test_with_progress_normal_mode(self) -> None:
        """Test with progress in normal mode."""
        prompts = FlextCliPrompts()
        items = [1, 2, 3]
        result = prompts.with_progress(items, "Processing items")
        assert result.is_success
        assert result.data == items

    def test_with_progress_empty_items(self) -> None:
        """Test with progress with empty items."""
        prompts = FlextCliPrompts()
        items: FlextTypes.List = []
        result = prompts.with_progress(items, "Processing items")
        assert result.is_success
        assert result.data == items

    def test_with_progress_exception(self) -> None:
        """Test with progress with exception."""
        prompts = FlextCliPrompts()
        items = [1, 2, 3]
        # Mock logger to raise exception
        with patch.object(prompts._logger, "info", side_effect=Exception("Test error")):
            result = prompts.with_progress(items, "Processing items")
            assert result.is_failure
            assert (
                result.error is not None
                and "Progress processing failed: Test error" in result.error
            )


class TestFlextCliPromptsIntegration:
    """Test integration scenarios."""

    def test_full_workflow_quiet_mode(self) -> None:
        """Test full workflow in quiet mode."""
        prompts = FlextCliPrompts(quiet=True)

        # Test all methods in quiet mode
        confirm_result = prompts.confirm("Continue?", default=True)
        assert confirm_result.is_success
        assert confirm_result.data is True

        prompt_result = prompts.prompt("Enter value", default="test")
        assert prompt_result.is_success
        assert prompt_result.data == "test"

        status_result = prompts.print_status("Status message")
        assert status_result.is_success

        progress_result = prompts.create_progress("Working...")
        assert progress_result.is_success

    def test_full_workflow_normal_mode(self) -> None:
        """Test full workflow in normal mode."""
        prompts = FlextCliPrompts()

        # Test all methods in normal mode (with mocked input)
        with patch("builtins.input", return_value="y"):
            confirm_result = prompts.confirm("Continue?")
            assert confirm_result.is_success
            assert confirm_result.data is True

        with patch("builtins.input", return_value="test_input"):
            prompt_result = prompts.prompt("Enter value")
            assert prompt_result.is_success
            assert prompt_result.data == "test_input"

        status_result = prompts.print_status("Status message")
        assert status_result.is_success

        progress_result = prompts.create_progress("Working...")
        assert progress_result.is_success
