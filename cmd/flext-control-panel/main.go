package main

import (
	"github.com/flext-sh/flext/pkg/flextservice"
)

func main() {
	// Define service-specific information
	serviceInfo := flextservice.ServiceInfo{
		Name:        "flext-control-panel",
		DefaultPort: 8081,
		Description: "FLEXT Control Panel",
	}

	// Launch service using common launcher
	flextservice.LaunchService(serviceInfo)
}