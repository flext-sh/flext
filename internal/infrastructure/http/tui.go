package http

// Bubble Tea TUI - Interface de terminal reativa
// Instalar: go get github.com/charmbracelet/bubbletea github.com/charmbracelet/lipgloss

/*
type Model struct {
	stats    map[string]int
	pipelines []string
	logs     []string
	selected int
}

func (m Model) Init() tea.Cmd {
	return tea.Tick(time.Second, func(time.Time) tea.Msg {
		return "update"
	})
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			return m, tea.Quit
		case "up":
			if m.selected > 0 {
				m.selected--
			}
		case "down":
			if m.selected < len(m.pipelines)-1 {
				m.selected++
			}
		case "enter":
			// Execute pipeline
			m.logs = append(m.logs, fmt.Sprintf("✅ Executed: %s", m.pipelines[m.selected]))
		}
	case string:
		// Auto-update
		m.stats["pipelines"] = rand.Intn(10)
		m.stats["jobs"] = rand.Intn(5)
		return m, tea.Tick(time.Second*5, func(time.Time) tea.Msg { return "update" })
	}
	return m, nil
}

func (m Model) View() string {
	style := lipgloss.NewStyle().Foreground(lipgloss.Color("#04B575"))
	header := style.Render("🚀 FLEXT Dashboard")
	
	// Stats
	stats := fmt.Sprintf(`
📈 Stats:
  Pipelines: %d
  Plugins: %d 
  Jobs: %d
`, m.stats["pipelines"], m.stats["plugins"], m.stats["jobs"])
	
	// Pipelines
	pipelineList := "📋 Pipelines:\n"
	for i, p := range m.pipelines {
		cursor := " "
		if i == m.selected {
			cursor = "> "
		}
		pipelineList += fmt.Sprintf("%s%s\n", cursor, p)
	}
	
	// Logs
	logsList := "📋 Logs:\n"
	for _, log := range m.logs {
		logsList += "  " + log + "\n"
	}
	
	return fmt.Sprintf("%s\n\n%s\n%s\n%s\n\nPress q to quit, enter to execute", 
		header, stats, pipelineList, logsList)
}

func StartTUI() {
	m := Model{
		stats: map[string]int{"pipelines": 3, "plugins": 8, "jobs": 2},
		pipelines: []string{"⚙️ ETL Pipeline", "🔄 Data Sync", "📈 Analytics"},
		logs: []string{"✅ Server started", "✅ Database connected"},
	}
	
	p := tea.NewProgram(m)
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error: %v", err)
		os.Exit(1)
	}
}
*/
