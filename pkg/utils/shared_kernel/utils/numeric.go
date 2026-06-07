package utils

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
