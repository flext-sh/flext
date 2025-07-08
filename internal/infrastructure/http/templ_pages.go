package http

import (
	"context"
	"io"
)

// DashboardPage gera a página do dashboard reativa
func DashboardPage(ctx context.Context, w io.Writer) error {
	return Layout("Dashboard", func(ctx context.Context, w io.Writer) error {
		// Header
		if err := dashboardHeader(ctx, w); err != nil {
			return err
		}

		// Stats cards
		if err := dashboardStats(ctx, w); err != nil {
			return err
		}

		// Activity and charts
		if err := dashboardContent(ctx, w); err != nil {
			return err
		}

		// Quick actions
		return dashboardActions(ctx, w)
	})(ctx, w)
}

func dashboardHeader(ctx context.Context, w io.Writer) error {
	return func(ctx context.Context, w io.Writer) error {
		_, err := w.Write([]byte(`
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 flex items-center">
                <i class="fas fa-tachometer-alt text-blue-500 mr-3"></i>
                FLEXT Dashboard
            </h1>
            <p class="text-gray-600 mt-2">Welcome to the FLEXT Framework Management Interface</p>
        </div>
`))
		return err
	}(ctx, w)
}

func dashboardStats(ctx context.Context, w io.Writer) error {
	return func(ctx context.Context, w io.Writer) error {
		_, err := w.Write([]byte(`
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
`))
		if err != nil {
			return err
		}

		// Pipeline card
		if err := StatCard("Pipelines", "fas fa-sitemap", "from-blue-500 to-blue-600", "0", "/web/pipelines")(ctx, w); err != nil {
			return err
		}

		// Plugin card
		if err := StatCard("Plugins", "fas fa-plug", "from-green-500 to-green-600", "0", "/web/plugins")(ctx, w); err != nil {
			return err
		}

		// Active jobs card
		if err := StatCard("Active Jobs", "fas fa-cog", "from-yellow-500 to-yellow-600", "0", "/web/monitoring")(ctx, w); err != nil {
			return err
		}

		// System status card
		if err := StatCard("System Status", "fas fa-server", "from-purple-500 to-purple-600", "Healthy", "/health")(ctx, w); err != nil {
			return err
		}

		_, err = w.Write([]byte(`
        </div>
`))
		return err
	}(ctx, w)
}

func dashboardContent(ctx context.Context, w io.Writer) error {
	return func(ctx context.Context, w io.Writer) error {
		_, err := w.Write([]byte(`
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <!-- Recent Activity -->
            <div class="lg:col-span-2">
`))
		if err != nil {
			return err
		}

		if err := Card("Recent Activity", "fas fa-list", func(ctx context.Context, w io.Writer) error {
			_, err := w.Write([]byte(`
                    <div hx-get="/api/activity/recent"
                         hx-trigger="load, every 15s"
                         hx-indicator="#activity-loading"
                         class="space-y-3">
                        <div id="activity-loading" class="text-center py-8">
                            <i class="fas fa-spinner fa-spin text-blue-500 text-2xl"></i>
                            <p class="text-gray-600 mt-2">Loading recent activity...</p>
                        </div>
                    </div>
`))
			return err
		})(ctx, w); err != nil {
			return err
		}

		_, err = w.Write([]byte(`
            </div>

            <!-- System Overview Chart -->
            <div>
`))
		if err != nil {
			return err
		}

		if err := Card("System Overview", "fas fa-chart-pie",
			Chart("overviewChart", "doughnut"),
		)(ctx, w); err != nil {
			return err
		}

		_, err = w.Write([]byte(`
            </div>
        </div>
`))
		return err
	}(ctx, w)
}

func dashboardActions(ctx context.Context, w io.Writer) error {
	return func(ctx context.Context, w io.Writer) error {
		if err := Card("Quick Actions", "fas fa-bolt", func(ctx context.Context, w io.Writer) error {
			_, err := w.Write([]byte(`
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
`))
			if err != nil {
				return err
			}

			// Quick action buttons
			if err := Button("Create Pipeline", "fas fa-plus", "window.location='/web/pipelines/new'", "primary")(ctx, w); err != nil {
				return err
			}

			if err := Button("Register Plugin", "fas fa-plug", "window.location='/web/plugins/new'", "success")(ctx, w); err != nil {
				return err
			}

			if err := Button("View Logs", "fas fa-file-alt", "window.location='/web/monitoring'", "warning")(ctx, w); err != nil {
				return err
			}

			if err := Button("Run Diagnostics", "fas fa-stethoscope", "runDiagnostics()", "danger")(ctx, w); err != nil {
				return err
			}

			_, err = w.Write([]byte(`
                    </div>
`))
			return err
		})(ctx, w); err != nil {
			return err
		}

		return nil
	}(ctx, w)
}

// PipelinesPage gera a página de pipelines
func PipelinesPage(ctx context.Context, w io.Writer) error {
	return Layout("Pipelines", func(ctx context.Context, w io.Writer) error {
		_, err := w.Write([]byte(`
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold text-gray-900 flex items-center">
                <i class="fas fa-sitemap text-blue-500 mr-3"></i>
                Pipelines
            </h1>
`))
		if err != nil {
			return err
		}

		if err := Button("Create Pipeline", "fas fa-plus", "window.location='/web/pipelines/new'", "primary")(ctx, w); err != nil {
			return err
		}

		_, err = w.Write([]byte(`
        </div>
`))
		if err != nil {
			return err
		}

		return Card("Pipeline List", "fas fa-list",
			Table([]string{"ID", "Name", "Status", "Steps", "Created", "Actions"}, "/api/pipelines/table"),
		)(ctx, w)
	})(ctx, w)
}

// PluginsPage gera a página de plugins
func PluginsPage(ctx context.Context, w io.Writer) error {
	return Layout("Plugins", func(ctx context.Context, w io.Writer) error {
		_, err := w.Write([]byte(`
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold text-gray-900 flex items-center">
                <i class="fas fa-plug text-green-500 mr-3"></i>
                Plugins
            </h1>
`))
		if err != nil {
			return err
		}

		if err := Button("Register Plugin", "fas fa-plus", "window.location='/web/plugins/new'", "success")(ctx, w); err != nil {
			return err
		}

		_, err = w.Write([]byte(`
        </div>
`))
		if err != nil {
			return err
		}

		return Card("Plugin Registry", "fas fa-list",
			Table([]string{"Name", "Type", "Version", "Status", "Description", "Actions"}, "/api/plugins/table"),
		)(ctx, w)
	})(ctx, w)
}

// MonitoringPage gera a página de monitoramento
func MonitoringPage(ctx context.Context, w io.Writer) error {
	return Layout("Monitoring", func(ctx context.Context, w io.Writer) error {
		_, err := w.Write([]byte(`
        <h1 class="text-3xl font-bold text-gray-900 flex items-center mb-8">
            <i class="fas fa-chart-line text-purple-500 mr-3"></i>
            Monitoring Dashboard
        </h1>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
`))
		if err != nil {
			return err
		}

		// Performance chart
		if err := Card("Performance Metrics", "fas fa-chart-line",
			Chart("performanceChart", "line"),
		)(ctx, w); err != nil {
			return err
		}

		// System logs
		if err := Card("System Logs", "fas fa-file-alt", func(ctx context.Context, w io.Writer) error {
			_, err := w.Write([]byte(`
                    <div hx-get="/api/logs/recent"
                         hx-trigger="load, every 10s"
                         hx-indicator="#logs-loading"
                         class="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm h-64 overflow-y-auto">
                        <div id="logs-loading" class="text-center py-8">
                            <i class="fas fa-spinner fa-spin"></i> Loading logs...
                        </div>
                    </div>
`))
			return err
		})(ctx, w); err != nil {
			return err
		}

		_, err = w.Write([]byte(`
        </div>
`))
		return err
	})(ctx, w)
}
