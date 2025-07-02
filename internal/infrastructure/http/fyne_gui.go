package http

// Fyne GUI - Interface nativa super simples
// Instalar: go get fyne.io/fyne/v2/app fyne.io/fyne/v2/widget

/*
func StartFyneGUI() {
	myApp := app.New()
	myWindow := myApp.NewWindow("FLEXT Dashboard")
	myWindow.Resize(fyne.NewSize(800, 600))

	// Stats cards
	statsContainer := container.NewGridWithColumns(3,
		widget.NewCard("Pipelines", "3", widget.NewProgressBar()),
		widget.NewCard("Plugins", "8", widget.NewProgressBar()),
		widget.NewCard("Jobs", "2", widget.NewProgressBar()),
	)

	// Pipeline list
	pipelineList := widget.NewList(
		func() int { return 3 },
		func() fyne.CanvasObject {
			return container.NewBorder(nil, nil,
				widget.NewLabel("Pipeline"), 
				widget.NewButton("▶️", nil),
				widget.NewLabel("Status"),
			)
		},
		func(id widget.ListItemID, obj fyne.CanvasObject) {
			// Update pipeline info
		},
	)

	// Logs
	logsText := widget.NewRichTextFromMarkdown(`
## 📋 Recent Logs
- ✅ Server started
- ✅ Database connected  
- ⚠️ High memory usage
- ✅ Pipeline executed
`)

	// Layout
	content := container.NewVBox(
		widget.NewLabel("🚀 FLEXT Dashboard"),
		statsContainer,
		container.NewHSplit(
			pipelineList,
			logsText,
		),
	)

	myWindow.SetContent(content)
	myWindow.ShowAndRun()
}
*/
