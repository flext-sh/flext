"""Tests for flext_tools.colors module.

Tests the color constants, formatting functions, and output utilities
to achieve 100% test coverage and validate proper functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

from unittest import mock
from unittest.mock import patch

from flext_tools.colors import Colors, colorize, print_colored


class TestColors:
    """Test the Colors class with all ANSI color constants."""

    def test_color_constants_exist(self) -> None:
        """Test that all expected color constants are defined."""
        # Test basic colors
        assert hasattr(Colors, "RED")
        assert hasattr(Colors, "GREEN")
        assert hasattr(Colors, "BLUE")
        assert hasattr(Colors, "YELLOW")
        assert hasattr(Colors, "CYAN")
        assert hasattr(Colors, "MAGENTA")
        assert hasattr(Colors, "WHITE")
        assert hasattr(Colors, "GRAY")
        assert hasattr(Colors, "ORANGE")

        # Test formatting
        assert hasattr(Colors, "BOLD")
        assert hasattr(Colors, "UNDERLINE")
        assert hasattr(Colors, "RESET")

        # Test semantic aliases
        assert hasattr(Colors, "WARNING")
        assert hasattr(Colors, "FAIL")
        assert hasattr(Colors, "HEADER")
        assert hasattr(Colors, "ENDC")

    def test_color_values_are_ansi_codes(self) -> None:
        """Test that color constants contain proper ANSI escape sequences."""
        assert Colors.RED.startswith("\033[")
        assert Colors.GREEN.startswith("\033[")
        assert Colors.BLUE.startswith("\033[")
        assert Colors.RESET == "\033[0m"
        assert Colors.BOLD == "\033[1m"
        assert Colors.UNDERLINE == "\033[4m"

    def test_semantic_color_mappings(self) -> None:
        """Test that semantic color names map to correct colors."""
        assert Colors.WARNING == Colors.YELLOW
        assert Colors.FAIL == Colors.RED
        assert Colors.HEADER == Colors.MAGENTA
        assert Colors.ENDC == Colors.RESET


class TestColorize:
    """Test the colorize function for text formatting."""

    def test_colorize_with_color(self) -> None:
        """Test colorizing text with a color code."""
        message = "Test message"
        color = Colors.GREEN
        result = colorize(message, color)

        expected = f"{color}{message}{Colors.RESET}"
        assert result == expected

    def test_colorize_without_color(self) -> None:
        """Test colorizing text without color (empty string)."""
        message = "Test message"
        result = colorize(message, "")

        # Should return message unchanged when no color provided
        assert result == message

    def test_colorize_with_empty_message(self) -> None:
        """Test colorizing empty message."""
        result = colorize("", Colors.RED)
        expected = f"{Colors.RED}{Colors.RESET}"
        assert result == expected

    def test_colorize_with_special_characters(self) -> None:
        """Test colorizing text with special characters."""
        message = "Test with\nnewlines\tand\ttabs"
        color = Colors.BLUE
        result = colorize(message, color)

        expected = f"{color}{message}{Colors.RESET}"
        assert result == expected

    def test_colorize_preserves_message_content(self) -> None:
        """Test that colorize doesn't modify the actual message content."""
        original_message = "Original message content"
        result = colorize(original_message, Colors.CYAN)

        # Should contain the original message
        assert original_message in result
        # Should start with color code
        assert result.startswith(Colors.CYAN)
        # Should end with reset code
        assert result.endswith(Colors.RESET)


class TestPrintColored:
    """Test the print_colored function for console output with logging."""

    @patch("flext_tools.colors.FlextCliFormatters")
    @patch("flext_tools.colors._logger")
    def test_print_colored_with_color(
        self, mock_logger: mock.Mock, mock_formatter_class: mock.Mock
    ) -> None:
        """Test print_colored with color outputs colored text and logs."""
        message = "Success message"
        color = Colors.GREEN
        mock_formatter = mock.Mock()
        mock_formatter_class.return_value = mock_formatter

        print_colored(message, color)

        # Should print the colorized text
        expected_colored = f"{color}{message}{Colors.RESET}"
        mock_formatter.console.print.assert_called_once_with(expected_colored)

        # Should log the original message (without color codes)
        mock_logger.info.assert_called_once_with(message)

    @patch("flext_tools.colors.FlextCliFormatters")
    @patch("flext_tools.colors._logger")
    def test_print_colored_without_color(
        self, mock_logger: mock.Mock, mock_formatter_class: mock.Mock
    ) -> None:
        """Test print_colored without color outputs plain text and logs."""
        message = "Plain message"
        mock_formatter = mock.Mock()
        mock_formatter_class.return_value = mock_formatter

        print_colored(message, "")

        # Should print the original message unchanged
        mock_formatter.console.print.assert_called_once_with(message)

        # Should log the original message
        mock_logger.info.assert_called_once_with(message)

    @patch("flext_tools.colors.FlextCliFormatters")
    @patch("flext_tools.colors._logger")
    def test_print_colored_logs_without_color_codes(
        self, mock_logger: mock.Mock, mock_formatter_class: mock.Mock
    ) -> None:
        """Test that logger receives message without ANSI color codes."""
        message = "Warning message"
        color = Colors.YELLOW
        mock_formatter = mock.Mock()
        mock_formatter_class.return_value = mock_formatter

        print_colored(message, color)

        # Logger should get the clean message without color codes
        mock_logger.info.assert_called_once_with(message)

        # Print should get the colored version
        expected_colored = f"{color}{message}{Colors.RESET}"
        mock_formatter.console.print.assert_called_once_with(expected_colored)

    @patch("flext_tools.colors.FlextCliFormatters")
    @patch("flext_tools.colors._logger")
    def test_print_colored_empty_message(
        self, mock_logger: mock.Mock, mock_formatter_class: mock.Mock
    ) -> None:
        """Test print_colored with empty message."""
        message = ""
        color = Colors.RED
        mock_formatter = mock.Mock()
        mock_formatter_class.return_value = mock_formatter

        print_colored(message, color)

        # Should print the colored empty string
        expected_colored = f"{color}{Colors.RESET}"
        mock_formatter.console.print.assert_called_once_with(expected_colored)

        # Should log the empty message
        mock_logger.info.assert_called_once_with(message)

    @patch("flext_tools.colors.FlextCliFormatters")
    @patch("flext_tools.colors._logger")
    def test_print_colored_with_multiline_message(
        self, mock_logger: mock.Mock, mock_formatter_class: mock.Mock
    ) -> None:
        """Test print_colored with multiline message."""
        message = "Line 1\nLine 2\nLine 3"
        color = Colors.BLUE
        mock_formatter = mock.Mock()
        mock_formatter_class.return_value = mock_formatter

        print_colored(message, color)

        # Should print the colorized multiline text
        expected_colored = f"{color}{message}{Colors.RESET}"
        mock_formatter.console.print.assert_called_once_with(expected_colored)

        # Should log the original multiline message
        mock_logger.info.assert_called_once_with(message)


class TestColorIntegration:
    """Integration tests for color functionality."""

    def test_color_integration_workflow(self) -> None:
        """Test a complete workflow using color functions."""
        # Test colorize for string composition
        warning_text = colorize("Warning: ", Colors.YELLOW)
        error_text = colorize("Error!", Colors.RED)

        # Both should be properly formatted
        assert warning_text.startswith(Colors.YELLOW)
        assert warning_text.endswith(Colors.RESET)
        assert error_text.startswith(Colors.RED)
        assert error_text.endswith(Colors.RESET)

        # Should contain original text
        assert "Warning: " in warning_text
        assert "Error!" in error_text

    @patch("flext_tools.colors.FlextCliFormatters")
    @patch("flext_tools.colors._logger")
    def test_print_colored_multiple_calls(
        self, mock_logger: mock.Mock, mock_formatter_class: mock.Mock
    ) -> None:
        """Test multiple calls to print_colored work correctly."""
        # Set up the mock
        mock_formatter = mock.Mock()
        mock_formatter_class.return_value = mock_formatter

        messages = [
            ("Success", Colors.GREEN),
            ("Warning", Colors.YELLOW),
            ("Error", Colors.RED),
            ("Info", ""),  # No color
        ]

        for message, color in messages:
            print_colored(message, color)

        # Should have called console.print and logger for each message
        assert mock_formatter.console.print.call_count == len(messages)
        assert mock_logger.info.call_count == len(messages)

        # Check the calls match expectations
        for i, (message, color) in enumerate(messages):
            expected_colored = colorize(message, color)
            assert mock_formatter.console.print.call_args_list[i][0][0] == expected_colored
            assert mock_logger.info.call_args_list[i][0][0] == message
