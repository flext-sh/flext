package utils

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
func (e Either[L, R]) Fold(leftF func(L) any, rightF func(R) any) any {
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
