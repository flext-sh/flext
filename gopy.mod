module github.com/flext-sh/flext/gopy

go 1.21

replace github.com/flext-sh/flext => ./

require github.com/flext-sh/flext v0.0.0-00010101000000-000000000000

// Transitive dependencies required for gopy compatibility
require (
	github.com/labstack/echo/v4 v4.13.4
	github.com/rs/zerolog v1.30.0
	github.com/pkg/errors v0.9.1
	github.com/go-playground/validator/v10 v10.22.0
)