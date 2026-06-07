package utils

import (
	"sort"
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
