package utils

import (
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/google/uuid"
)

// ToJSON converts value to JSON string
func ToJSON(v any) (string, error) {
	bytes, err := json.Marshal(v)
	if err != nil {
		return "", fmt.Errorf("failed to marshal to JSON: %w", err)
	}
	return string(bytes), nil
}

// FromJSON parses JSON string into value
func FromJSON[T any](jsonStr string) (T, error) {
	var result T
	err := json.Unmarshal([]byte(jsonStr), &result)
	if err != nil {
		return result, fmt.Errorf("failed to unmarshal from JSON: %w", err)
	}
	return result, nil
}

// ToString converts value to string representation
func ToString(v any) string {
	result := ""
	if v != nil {
		switch val := v.(type) {
		case string:
			result = val
		case fmt.Stringer:
			result = val.String()
		case error:
			result = val.Error()
		case bool:
			result = strconv.FormatBool(val)
		case uuid.UUID:
			result = val.String()
		case time.Time:
			result = val.Format(time.RFC3339)
		default:
			result = fmt.Sprintf("%v", val)
		}
	}
	return result
}

// ToStringSlice converts slice of any type to string slice
func ToStringSlice[T any](slice []T) []string {
	return Map(slice, func(v T) string {
		return ToString(v)
	})
}
