#!/bin/bash

# Create a completely isolated virtual environment
VENV_PATH="/home/marlonsc/pyauto/.venv_isolated"
REPO_PATH="/home/marlonsc/pyauto/dc-api-x"

echo "Creating isolated virtual environment at $VENV_PATH..."
python3 -m venv "$VENV_PATH" --clear --without-pip

# Install pip using the get-pip.py method to ensure isolation
echo "Installing pip..."
curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
"$VENV_PATH/bin/python" /tmp/get-pip.py --force-reinstall
rm /tmp/get-pip.py

# Activate the environment
source "$VENV_PATH/bin/activate"

# Ensure pip and setuptools are up to date
pip install --upgrade pip setuptools wheel

# Install compatible versions of pydantic and related packages
echo "Installing compatible package versions..."
pip install pydantic==2.0.3 pydantic-core==2.3.0 pydantic-settings==2.0.3 python-dotenv==1.0.0

# Install remaining dependencies
echo "Installing remaining dependencies..."
pip install requests==2.31.0 httpx==0.24.1 typer==0.9.0 rich==13.3.5 structlog==23.1.0 pluggy==1.0.0

# Install DCApiX in editable mode
echo "Installing dc-api-x in development mode..."
pip install -e "$REPO_PATH"

# Create a wrapper script to use the isolated environment
WRAPPER_PATH="/home/marlonsc/pyauto/run_dcapix.sh"
cat >"$WRAPPER_PATH" <<'EOF'
#!/bin/bash
source "$HOME/pyauto/.venv_isolated/bin/activate"
dcapix "$@"
EOF

chmod +x "$WRAPPER_PATH"

echo ""
echo "Setup complete. To use dcapix, run:"
echo "/home/marlonsc/pyauto/run_dcapix.sh"
