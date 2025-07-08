package http

import (
	"context"
	"fmt"
	"io"

	"github.com/labstack/echo/v4"
)

// Component representa um componente reativo
type Component func(ctx context.Context, w io.Writer) error

// Layout cria o layout base da aplicação
func Layout(title string, content Component) Component {
	return func(ctx context.Context, w io.Writer) error {
		_, err := fmt.Fprintf(w, `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%s - FLEXT</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-blue-600 text-white shadow-lg">
        <div class="container mx-auto px-4">
            <div class="flex justify-between items-center h-16">
                <div class="flex items-center space-x-4">
                    <a href="/web" class="flex items-center space-x-2 text-xl font-bold">
                        <i class="fas fa-cogs text-yellow-400"></i>
                        <span>FLEXT</span>
                    </a>
                    <div class="hidden md:flex space-x-4">
                        <a href="/web" class="hover:bg-blue-700 px-3 py-2 rounded transition">Dashboard</a>
                        <a href="/web/pipelines" class="hover:bg-blue-700 px-3 py-2 rounded transition">Pipelines</a>
                        <a href="/web/plugins" class="hover:bg-blue-700 px-3 py-2 rounded transition">Plugins</a>
                        <a href="/web/monitoring" class="hover:bg-blue-700 px-3 py-2 rounded transition">Monitoring</a>
                    </div>
                </div>
                <div class="flex items-center space-x-4">
                    <span hx-get="/api/health" hx-trigger="every 30s" class="text-sm">System Status: <span class="text-green-400">Healthy</span></span>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
`, title)
		if err != nil {
			return err
		}

		if err := content(ctx, w); err != nil {
			return err
		}

		_, err = fmt.Fprint(w, `
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t mt-12">
        <div class="container mx-auto px-4 py-6 text-center text-gray-600">
            <p>&copy; 2025 FLEXT Framework v2.0.0</p>
        </div>
    </footer>
</body>
</html>
`)
		return err
	}
}

// Card cria um cartão reativo
func Card(title, icon string, children ...Component) Component {
	return func(ctx context.Context, w io.Writer) error {
		_, err := fmt.Fprintf(w, `
        <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
            <div class="px-6 py-4 border-b border-gray-200">
                <h3 class="text-lg font-semibold text-gray-800 flex items-center">
                    <i class="%s mr-2"></i> %s
                </h3>
            </div>
            <div class="p-6">
`, icon, title)
		if err != nil {
			return err
		}

		for _, child := range children {
			if err := child(ctx, w); err != nil {
				return err
			}
		}

		_, err = fmt.Fprint(w, `
            </div>
        </div>
`)
		return err
	}
}

// StatCard cria um cartão de estatística reativo
func StatCard(title, icon, color, value, link string) Component {
	return func(ctx context.Context, w io.Writer) error {
		_, err := fmt.Fprintf(w, `
        <div class="bg-gradient-to-r %s text-white rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
             x-data="{ animated: false }"
             x-init="setTimeout(() => animated = true, 100)"
             :class="animated ? 'scale-100 opacity-100' : 'scale-95 opacity-0'">
            <div class="p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm opacity-90">%s</p>
                        <p class="text-3xl font-bold"
                           hx-get="/api/stats/%s"
                           hx-trigger="load, every 15s"
                           hx-swap="innerHTML">%s</p>
                    </div>
                    <div class="text-4xl opacity-80">
                        <i class="%s"></i>
                    </div>
                </div>
                <div class="mt-4">
                    <a href="%s" class="text-sm opacity-90 hover:opacity-100 transition">
                        View details <i class="fas fa-arrow-right ml-1"></i>
                    </a>
                </div>
            </div>
        </div>
`, color, title, title, value, icon, link)
		return err
	}
}

// Button cria um botão reativo
func Button(text, icon, action, variant string) Component {
	return func(ctx context.Context, w io.Writer) error {
		colorClass := "bg-blue-500 hover:bg-blue-600"
		switch variant {
		case "success":
			colorClass = "bg-green-500 hover:bg-green-600"
		case "warning":
			colorClass = "bg-yellow-500 hover:bg-yellow-600"
		case "danger":
			colorClass = "bg-red-500 hover:bg-red-600"
		}

		_, err := fmt.Fprintf(w, `
        <button class="%s text-white px-4 py-2 rounded-lg transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-300"
                x-data="{ loading: false }"
                @click="loading = true; %s; setTimeout(() => loading = false, 2000)"
                :disabled="loading"
                :class="loading ? 'opacity-75 cursor-not-allowed' : ''">
            <i class="%s mr-2" :class="loading ? 'fa-spin fa-spinner' : ''"></i>
            <span x-text="loading ? 'Processing...' : '%s'"></span>
        </button>
`, colorClass, action, icon, text)
		return err
	}
}

// Table cria uma tabela reativa
func Table(headers []string, endpoint string) Component {
	return func(ctx context.Context, w io.Writer) error {
		_, err := fmt.Fprint(w, `
        <div class="overflow-x-auto">
            <table class="min-w-full bg-white border border-gray-200 rounded-lg">
                <thead class="bg-gray-50">
                    <tr>
`)
		if err != nil {
			return err
		}

		for _, header := range headers {
			_, err := fmt.Fprintf(w, `                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">%s</th>\n`, header)
			if err != nil {
				return err
			}
		}

		_, err = fmt.Fprintf(w, `
                    </tr>
                </thead>
                <tbody hx-get="%s"
                       hx-trigger="load, every 30s"
                       hx-indicator="#table-loading"
                       class="bg-white divide-y divide-gray-200">
                    <tr id="table-loading">
                        <td colspan="%d" class="px-6 py-4 text-center text-gray-500">
                            <i class="fas fa-spinner fa-spin mr-2"></i> Loading...
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
`, endpoint, len(headers))
		return err
	}
}

// Chart cria um gráfico reativo
func Chart(chartId, chartType string) Component {
	return func(ctx context.Context, w io.Writer) error {
		_, err := fmt.Fprintf(w, `
        <div class="relative">
            <canvas id="%s"
                    class="w-full h-64"
                    x-data="chart('%s', '%s')"
                    x-init="initChart()"
                    hx-get="/api/charts/%s/data"
                    hx-trigger="load, every 60s"
                    hx-swap="none"
                    @htmx:after-request="updateChart($event.detail.xhr.response)"></canvas>
        </div>
`, chartId, chartId, chartType, chartId)
		return err
	}
}

// Form cria um formulário reativo
func Form(action, method string, children ...Component) Component {
	return func(ctx context.Context, w io.Writer) error {
		_, err := fmt.Fprintf(w, `
        <form hx-%s="%s"
              hx-swap="outerHTML"
              hx-indicator="#form-loading"
              class="space-y-4"
              x-data="{ submitting: false }"
              @htmx:before-request="submitting = true"
              @htmx:after-request="submitting = false">
`, method, action)
		if err != nil {
			return err
		}

		for _, child := range children {
			if err := child(ctx, w); err != nil {
				return err
			}
		}

		_, err = fmt.Fprint(w, `
            <div id="form-loading" class="htmx-indicator text-center">
                <i class="fas fa-spinner fa-spin text-blue-500"></i>
                <span class="ml-2 text-gray-600">Processing...</span>
            </div>
        </form>
`)
		return err
	}
}

// Input cria um campo de entrada
func Input(name, placeholder, inputType string) Component {
	return func(ctx context.Context, w io.Writer) error {
		_, err := fmt.Fprintf(w, `
            <div>
                <input type="%s"
                       name="%s"
                       placeholder="%s"
                       class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                       required>
            </div>
`, inputType, name, placeholder)
		return err
	}
}

// TemplRenderer implementa um renderer personalizado para Echo
type TemplRenderer struct{}

func (t *TemplRenderer) Render(w io.Writer, name string, data interface{}, c echo.Context) error {
	ctx := c.Request().Context()

	switch name {
	case "dashboard":
		return DashboardPage(ctx, w)
	case "pipelines":
		return PipelinesPage(ctx, w)
	case "plugins":
		return PluginsPage(ctx, w)
	case "monitoring":
		return MonitoringPage(ctx, w)
	default:
		return fmt.Errorf("template not found: %s", name)
	}
}
