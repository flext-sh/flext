#!/bin/bash

# PHASE 1.3: Baseline Quality Metrics Collection Script

echo "=== FLEXT ECOSYSTEM BASELINE QUALITY METRICS ===" >/tmp/baseline_metrics.txt
echo "Date: $(date)" >>/tmp/baseline_metrics.txt
echo "" >>/tmp/baseline_metrics.txt

# Core projects
for project in flext-core flext-meltano flext-api flext-cli flext-ldap flext-ldif; do
	if [ -d "$project" ]; then
		cd "$project"
		echo "=== $project ===" >>/tmp/baseline_metrics.txt

		# Ruff check
		ruff_result=$(ruff check src 2>&1 | tail -1)
		echo "Ruff: $ruff_result" >>/tmp/baseline_metrics.txt

		# Pytest status
		if [ -d "tests" ]; then
			test_result=$(poetry run pytest tests/ -q --tb=no 2>&1 | tail -1)
			echo "Tests: $test_result" >>/tmp/baseline_metrics.txt
		fi

		echo "" >>/tmp/baseline_metrics.txt
		cd ..
	fi
done

# Singer projects (taps and targets)
for project in flext-tap-* flext-target-* flext-dbt-*; do
	if [ -d "$project" ]; then
		cd "$project"
		echo "=== $project ===" >>/tmp/baseline_metrics.txt

		# Ruff check
		ruff_result=$(ruff check src 2>&1 | tail -1)
		echo "Ruff: $ruff_result" >>/tmp/baseline_metrics.txt

		echo "" >>/tmp/baseline_metrics.txt
		cd ..
	fi
done

cat /tmp/baseline_metrics.txt
