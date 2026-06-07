package validation

import (
	"regexp"
	"strings"
	"unicode"
)

// SanitizeString removes dangerous characters and trims whitespace
func SanitizeString(input string) string {
	sanitized := strings.TrimSpace(input)
	sanitized = strings.ReplaceAll(sanitized, "\x00", "")

	var result strings.Builder
	for _, r := range sanitized {
		if unicode.IsPrint(r) || r == '\n' || r == '\t' {
			result.WriteRune(r)
		}
	}

	return result.String()
}

// SanitizeName sanitizes names for identifiers
func SanitizeName(input string) string {
	sanitized := SanitizeString(input)
	sanitized = strings.ToLower(sanitized)

	spacePattern := regexp.MustCompile(`\s+`)
	sanitized = spacePattern.ReplaceAllString(sanitized, " ")
	sanitized = strings.ReplaceAll(sanitized, " ", "-")

	unicodeMap := map[rune]string{
		'á': "a", 'à': "a", 'ä': "a", 'ã': "a", 'â': "a",
		'é': "e", 'è': "e", 'ë': "e", 'ê': "e",
		'í': "i", 'ì': "i", 'ï': "i", 'î': "i",
		'ó': "o", 'ò': "o", 'ö': "o", 'õ': "o", 'ô': "o",
		'ú': "u", 'ù': "u", 'ü': "u", 'û': "u",
		'ç': "c", 'ñ': "n",
	}

	var result strings.Builder
	for _, r := range sanitized {
		if replacement, ok := unicodeMap[r]; ok {
			result.WriteString(replacement)
		} else if unicode.IsLetter(r) || unicode.IsDigit(r) || r == '-' || r == '_' {
			result.WriteRune(r)
		}
	}

	return strings.Trim(result.String(), "-_")
}
