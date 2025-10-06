package main

import (
	"github.com/flext-sh/flext/pkg/flextservice"
)

func main() {
	// Define service-specific information
	serviceInfo := flextservice.ServiceInfo{
		Name:        "flext-server",
		DefaultPort: 8081,
		Description: "FLEXT Server",
	}

	// Launch service using common launcher
	flextservice.LaunchService(serviceInfo)
}
