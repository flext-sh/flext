package utils

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
