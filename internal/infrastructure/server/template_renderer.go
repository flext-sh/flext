package server

import (
	"html/template"
	"io"
	"path/filepath"

	"github.com/labstack/echo/v4"
)

// TemplateRenderer implements echo.Renderer for HTML templates
type TemplateRenderer struct {
	templates *template.Template
}

// NewTemplateRenderer creates a new template renderer
func NewTemplateRenderer(templatesDir string) (*TemplateRenderer, error) {
	// Parse all HTML templates in the templates directory
	tmpl, err := template.ParseGlob(filepath.Join(templatesDir, "*.html"))
	if err != nil {
		return nil, err
	}

	return &TemplateRenderer{
		templates: tmpl,
	}, nil
}

// Render executes template rendering
func (t *TemplateRenderer) Render(w io.Writer, name string, data interface{}, c echo.Context) error {
	return t.templates.ExecuteTemplate(w, name, data)
}
