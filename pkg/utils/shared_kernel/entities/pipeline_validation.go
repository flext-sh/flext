package entities

import "errors"

// Validate validates the pipeline
func (p *UnifiedPipeline) Validate() error {
	var err error
	switch {
	case p.Name == "":
		err = errors.New("name is required")
	case p.Owner == "":
		err = errors.New("owner is required")
	case len(p.Steps) == 0:
		err = errors.New("at least one step is required")
	}
	return err
}
