package utils

import "strings"

// StringMap applies function f to each string in slice
func StringMap(slice []string, f func(string) string) []string {
	return Map(slice, f)
}

// StringFilter filters strings based on predicate f
func StringFilter(slice []string, f func(string) bool) []string {
	return Filter(slice, f)
}

// TrimSpace trims whitespace from all strings in slice
func TrimSpace(slice []string) []string {
	return StringMap(slice, strings.TrimSpace)
}

// ToLower converts all strings to lowercase
func ToLower(slice []string) []string {
	return StringMap(slice, strings.ToLower)
}

// ToUpper converts all strings to uppercase
func ToUpper(slice []string) []string {
	return StringMap(slice, strings.ToUpper)
}

// NonEmpty filters out empty strings
func NonEmpty(slice []string) []string {
	return StringFilter(slice, func(s string) bool { return s != "" })
}

// Contains checks if slice contains specific string
func Contains(slice []string, target string) bool {
	return object(slice, func(s string) bool { return s == target })
}

// ContainsIgnoreCase checks if slice contains string (case-insensitive)
func ContainsIgnoreCase(slice []string, target string) bool {
	lowerTarget := strings.ToLower(target)
	return object(slice, func(s string) bool {
		return strings.ToLower(s) == lowerTarget
	})
}

// Join joins strings with separator
func Join(slice []string, separator string) string {
	return strings.Join(slice, separator)
}

// Split splits string by separator into slice
func Split(s, separator string) []string {
	if s == "" {
		return []string{}
	}
	return strings.Split(s, separator)
}
