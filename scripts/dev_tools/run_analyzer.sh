#!/bin/bash
# FLX Analyzer - Simplified Runner
# ─────────────────────────────────
# Simple wrapper to run the FLX Analyzer

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Print header
echo "════════════════════════════════════════════"
echo "  FLX Analyzer - Code Analysis Tool"
echo "════════════════════════════════════════════"
echo

# Check for Python
if [ -z "$(command -v python3)" ]; then
    echo "❌ Error: Python 3 is required but not found"
    exit 1
fi

echo "🔍 Running FLX Analyzer..."

# Run the analyzer with all arguments passed through
PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH" python3 -m flx_analyzer --function-call-analysis "$@"
RESULT=$?

# Check if successful
if [ $RESULT -eq 0 ]; then
    echo "✅ Analysis complete"
    
    # Find latest report directory (exclude dashboard directories)
    LATEST_REPORT=$(find ./reports -maxdepth 1 -type d -name "[0-9]*_[0-9]*" | sort -r | head -n 1)
    
    if [ -n "$LATEST_REPORT" ] && [ "$LATEST_REPORT" != "./reports" ]; then
        echo "📊 Reports generated in: $LATEST_REPORT"
        
        # Generate dashboard directly in the reports directory
        echo "🔄 Generating dashboard..."
        DASHBOARD_OUTPUT=$(python3 -m dc_analyzer.utils.dashboard "$LATEST_REPORT" 2>&1)
        
        if [ $? -eq 0 ]; then
            # Extract dashboard path from output
            DASHBOARD_PATH=$(echo "$DASHBOARD_OUTPUT" | grep "Dashboard generated:" | sed 's/Dashboard generated: //')
            
            if [ -n "$DASHBOARD_PATH" ] && [ -f "$DASHBOARD_PATH" ]; then
                echo "📊 Dashboard generated: $DASHBOARD_PATH"
                
                # Try to open the dashboard automatically
                if [ -n "$(command -v xdg-open 2>/dev/null)" ]; then
                    echo "🌐 Opening dashboard in browser..."
                    xdg-open "$DASHBOARD_PATH" >/dev/null 2>&1 || echo "⚠️ Could not open browser automatically"
                elif [ -n "$(command -v open 2>/dev/null)" ]; then
                    echo "🌐 Opening dashboard in browser..."
                    open "$DASHBOARD_PATH" || echo "⚠️ Could not open browser automatically"
                else
                    echo "🌐 Dashboard available at: $DASHBOARD_PATH"
                fi
            else
                echo "⚠️ Dashboard path not found in output"
            fi
        else
            echo "⚠️ Dashboard generation failed, but reports are available"
        fi
        
        echo "📈 Analysis complete. Check the reports directory for results."
    else
        echo "⚠️ No report directory found"
    fi
else
    echo "❌ Analysis failed"
    exit 1
fi
