package utils

import (
	"encoding/json"
	"fmt"
	"reflect"
	"sort"
	"strings"
	"time"

	"github.com/google/uuid"
)

// Functional programming utilities for Go

// Map applies function f to each element of slice and returns new slice
func Map[T, U any](slice []T, f func(T) U) []U {
	result := make([]U, len(slice))
	for i, v := range slice {
		result[i] = f(v)
	}
	return result
}

// MapWithIndex applies function f to each element with its index
func MapWithIndex[T, U any](slice []T, f func(T, int) U) []U {
	result := make([]U, len(slice))
	for i, v := range slice {
		result[i] = f(v, i)
	}
	return result
}

// Filter returns a new slice containing only elements that satisfy predicate f
func Filter[T any](slice []T, f func(T) bool) []T {
	result := make([]T, 0, len(slice))
	for _, v := range slice {
		if f(v) {
			result = append(result, v)
		}
	}
	return result
}

// FilterWithIndex filters elements based on predicate that receives value and index
func FilterWithIndex[T any](slice []T, f func(T, int) bool) []T {
	result := make([]T, 0, len(slice))
	for i, v := range slice {
		if f(v, i) {
			result = append(result, v)
		}
	}
	return result
}

// Reduce applies function f against accumulator and each element (left-to-right)
func Reduce[T, U any](slice []T, f func(U, T) U, initial U) U {
	result := initial
	for _, v := range slice {
		result = f(result, v)
	}
	return result
}

// Find returns the first element that satisfies predicate f
func Find[T any](slice []T, f func(T) bool) (T, bool) {
	var zero T
	for _, v := range slice {
		if f(v) {
			return v, true
		}
	}
	return zero, false
}

// FindIndex returns the index of first element that satisfies predicate f
func FindIndex[T any](slice []T, f func(T) bool) int {
	for i, v := range slice {
		if f(v) {
			return i
		}
	}
	return -1
}

// object returns true if at least one element satisfies predicate f
func object[T any](slice []T, f func(T) bool) bool {
	for _, v := range slice {
		if f(v) {
			return true
		}
	}
	return false
}

// All returns true if all elements satisfy predicate f
func All[T any](slice []T, f func(T) bool) bool {
	for _, v := range slice {
		if !f(v) {
			return false
		}
	}
	return true
}

// GroupBy groups elements by the result of key function f
func GroupBy[T any, K comparable](slice []T, f func(T) K) map[K][]T {
	result := make(map[K][]T)
	for _, v := range slice {
		key := f(v)
		result[key] = append(result[key], v)
	}
	return result
}

// Partition splits slice into two slices based on predicate f
func Partition[T any](slice []T, f func(T) bool) ([]T, []T) {
	var truthy, falsy []T
	for _, v := range slice {
		if f(v) {
			truthy = append(truthy, v)
		} else {
			falsy = append(falsy, v)
		}
	}
	return truthy, falsy
}

// Unique returns slice with unique elements
func Unique[T comparable](slice []T) []T {
	seen := make(map[T]bool)
	result := make([]T, 0, len(slice))
	for _, v := range slice {
		if !seen[v] {
			seen[v] = true
			result = append(result, v)
		}
	}
	return result
}

// UniqueBy returns slice with unique elements based on key function f
func UniqueBy[T any, K comparable](slice []T, f func(T) K) []T {
	seen := make(map[K]bool)
	result := make([]T, 0, len(slice))
	for _, v := range slice {
		key := f(v)
		if !seen[key] {
			seen[key] = true
			result = append(result, v)
		}
	}
	return result
}

// Chunk splits slice into chunks of specified size
func Chunk[T any](slice []T, size int) [][]T {
	if size <= 0 {
		return nil
	}

	var result [][]T
	for i := 0; i < len(slice); i += size {
		end := i + size
		if end > len(slice) {
			end = len(slice)
		}
		result = append(result, slice[i:end])
	}
	return result
}

// Zip combines multiple slices into slice of tuples
func Zip[T, U any](slice1 []T, slice2 []U) []struct {
	First  T
	Second U
} {
	minLen := len(slice1)
	if len(slice2) < minLen {
		minLen = len(slice2)
	}

	result := make([]struct {
		First  T
		Second U
	}, minLen)
	for i := 0; i < minLen; i++ {
		result[i] = struct {
			First  T
			Second U
		}{slice1[i], slice2[i]}
	}
	return result
}

// Flatten flattens nested slices into single slice
func Flatten[T any](slices [][]T) []T {
	var result []T
	for _, slice := range slices {
		result = append(result, slice...)
	}
	return result
}

// Reverse returns slice with elements in reverse order
func Reverse[T any](slice []T) []T {
	result := make([]T, len(slice))
	for i, v := range slice {
		result[len(slice)-1-i] = v
	}
	return result
}

// Sort sorts slice using provided comparison function
func Sort[T any](slice []T, less func(T, T) bool) []T {
	result := make([]T, len(slice))
	copy(result, slice)
	sort.Slice(result, func(i, j int) bool {
		return less(result[i], result[j])
	})
	return result
}

// SortBy sorts slice by the result of key function f
func SortBy[T any, K interface{ ~int | ~string | ~float64 }](slice []T, f func(T) K) []T {
	result := make([]T, len(slice))
	copy(result, slice)
	sort.Slice(result, func(i, j int) bool {
		return f(result[i]) < f(result[j])
	})
	return result
}

// String utilities

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

// Numeric utilities

// Sum returns sum of numeric slice
func Sum[T interface{ ~int | ~int64 | ~float64 }](slice []T) T {
	return Reduce(slice, func(acc, v T) T { return acc + v }, 0)
}

// Average returns average of numeric slice
func Average[T interface{ ~int | ~int64 | ~float64 }](slice []T) float64 {
	if len(slice) == 0 {
		return 0
	}
	return float64(Sum(slice)) / float64(len(slice))
}

// Min returns minimum value in slice
func Min[T interface {
	~int | ~int64 | ~float64 | ~string
}](slice []T) T {
	if len(slice) == 0 {
		var zero T
		return zero
	}
	return Reduce(slice[1:], func(acc, v T) T {
		if v < acc {
			return v
		}
		return acc
	}, slice[0])
}

// Max returns maximum value in slice
func Max[T interface {
	~int | ~int64 | ~float64 | ~string
}](slice []T) T {
	if len(slice) == 0 {
		var zero T
		return zero
	}
	return Reduce(slice[1:], func(acc, v T) T {
		if v > acc {
			return v
		}
		return acc
	}, slice[0])
}

// Type conversion utilities

// ToJSON converts value to JSON string
func ToJSON(v interface{}) (string, error) {
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
func ToString(v interface{}) string {
	if v == nil {
		return ""
	}

	switch val := v.(type) {
	case string:
		return val
	case fmt.Stringer:
		return val.String()
	case error:
		return val.Error()
	case bool:
		if val {
			return "true"
		}
		return "false"
	case uuid.UUID:
		return val.String()
	case time.Time:
		return val.Format(time.RFC3339)
	default:
		return fmt.Sprintf("%v", val)
	}
}

// ToStringSlice converts slice of any type to string slice
func ToStringSlice[T any](slice []T) []string {
	return Map(slice, func(v T) string {
		return ToString(v)
	})
}

// Identity returns the input value unchanged (useful for generic functions)
func Identity[T any](v T) T {
	return v
}

// Pipe applies functions in sequence (function composition)
func Pipe[T any](value T, functions ...func(T) T) T {
	result := value
	for _, f := range functions {
		result = f(result)
	}
	return result
}

// Curry converts function with 2 parameters into curried function
func Curry[T, U, V any](f func(T, U) V) func(T) func(U) V {
	return func(t T) func(U) V {
		return func(u U) V {
			return f(t, u)
		}
	}
}

// Memoize caches results of expensive function calls
func Memoize[T comparable, U any](f func(T) U) func(T) U {
	cache := make(map[T]U)
	return func(t T) U {
		if result, exists := cache[t]; exists {
			return result
		}
		result := f(t)
		cache[t] = result
		return result
	}
}

// Optional/Maybe type utilities

// Optional represents a value that may or may not exist
type Optional[T any] struct {
	value   T
	present bool
}

// Some creates an Optional with a value
func Some[T any](value T) Optional[T] {
	return Optional[T]{value: value, present: true}
}

// None creates an empty Optional
func None[T any]() Optional[T] {
	return Optional[T]{present: false}
}

// IsPresent returns true if Optional has a value
func (o Optional[T]) IsPresent() bool {
	return o.present
}

// IsEmpty returns true if Optional is empty
func (o Optional[T]) IsEmpty() bool {
	return !o.present
}

// Get returns the value if present, panics if empty
func (o Optional[T]) Get() T {
	if !o.present {
		panic("Optional is empty")
	}
	return o.value
}

// GetOrElse returns the value if present, otherwise returns default
func (o Optional[T]) GetOrElse(defaultValue T) T {
	if o.present {
		return o.value
	}
	return defaultValue
}

// Map applies function f to the value if present
func (o Optional[T]) Map(f func(T) T) Optional[T] {
	if !o.present {
		return None[T]()
	}
	return Some(f(o.value))
}

// FlatMap applies function f that returns an Optional
func (o Optional[T]) FlatMap(f func(T) Optional[T]) Optional[T] {
	if !o.present {
		return None[T]()
	}
	return f(o.value)
}

// Filter returns Optional if value satisfies predicate, otherwise None
func (o Optional[T]) Filter(f func(T) bool) Optional[T] {
	if !o.present || !f(o.value) {
		return None[T]()
	}
	return o
}

// Reflection utilities

// GetFieldValue gets field value from struct using reflection
func GetFieldValue(obj interface{}, fieldName string) (interface{}, error) {
	val := reflect.ValueOf(obj)
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}

	if val.Kind() != reflect.Struct {
		return nil, fmt.Errorf("object is not a struct")
	}

	field := val.FieldByName(fieldName)
	if !field.IsValid() {
		return nil, fmt.Errorf("field %s not found", fieldName)
	}

	return field.Interface(), nil
}

// SetFieldValue sets field value on struct using reflection
func SetFieldValue(obj interface{}, fieldName string, value interface{}) error {
	val := reflect.ValueOf(obj)
	if val.Kind() != reflect.Ptr {
		return fmt.Errorf("object must be a pointer")
	}

	val = val.Elem()
	if val.Kind() != reflect.Struct {
		return fmt.Errorf("object is not a struct")
	}

	field := val.FieldByName(fieldName)
	if !field.IsValid() {
		return fmt.Errorf("field %s not found", fieldName)
	}

	if !field.CanSet() {
		return fmt.Errorf("field %s cannot be set", fieldName)
	}

	fieldValue := reflect.ValueOf(value)
	if !fieldValue.Type().AssignableTo(field.Type()) {
		return fmt.Errorf("value type %s not assignable to field type %s",
			fieldValue.Type(), field.Type())
	}

	field.Set(fieldValue)
	return nil
}

// GetStructFields returns all field names of a struct
func GetStructFields(obj interface{}) []string {
	val := reflect.ValueOf(obj)
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}

	if val.Kind() != reflect.Struct {
		return nil
	}

	typ := val.Type()
	fields := make([]string, typ.NumField())
	for i := 0; i < typ.NumField(); i++ {
		fields[i] = typ.Field(i).Name
	}
	return fields
}

// Either type for error handling

// Either represents a value that can be either a value (Right) or an error (Left)
type Either[L, R any] struct {
	left    L
	right   R
	isRight bool
}

// Left creates an Either with a left value (typically an error)
func Left[L, R any](left L) Either[L, R] {
	return Either[L, R]{left: left, isRight: false}
}

// Right creates an Either with a right value (typically a success value)
func Right[L, R any](right R) Either[L, R] {
	return Either[L, R]{right: right, isRight: true}
}

// IsLeft returns true if Either contains a left value
func (e Either[L, R]) IsLeft() bool {
	return !e.isRight
}

// IsRight returns true if Either contains a right value
func (e Either[L, R]) IsRight() bool {
	return e.isRight
}

// GetLeft returns the left value, panics if right
func (e Either[L, R]) GetLeft() L {
	if e.isRight {
		panic("Either is Right")
	}
	return e.left
}

// GetRight returns the right value, panics if left
func (e Either[L, R]) GetRight() R {
	if !e.isRight {
		panic("Either is Left")
	}
	return e.right
}

// MapRight applies function f to right value
func (e Either[L, R]) MapRight(f func(R) R) Either[L, R] {
	if !e.isRight {
		return e
	}
	return Right[L, R](f(e.right))
}

// MapLeft applies function f to left value
func (e Either[L, R]) MapLeft(f func(L) L) Either[L, R] {
	if e.isRight {
		return e
	}
	return Left[L, R](f(e.left))
}

// Fold applies leftF to left value or rightF to right value
func (e Either[L, R]) Fold(leftF func(L) interface{}, rightF func(R) interface{}) interface{} {
	if e.isRight {
		return rightF(e.right)
	}
	return leftF(e.left)
}

// ToResult converts Either to Go's typical (value, error) pattern
func (e Either[error, R]) ToResult() (R, error) {
	if e.isRight {
		var zero error
		return e.right, zero
	}
	var zero R
	return zero, e.left
}

// FromResult creates Either from Go's typical (value, error) pattern
func FromResult[R any](value R, err error) Either[error, R] {
	if err != nil {
		return Left[error, R](err)
	}
	return Right[error, R](value)
}
