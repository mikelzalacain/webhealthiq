$ErrorActionPreference = "Stop"

# Create a virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
$env:VIRTUAL_ENV = "$PWD\venv"
$env:Path = "$PWD\venv\Scripts;$env:Path"

# Install requirements
Write-Host "Installing requirements..."
pip install -r backend\requirements.txt

# Run the FastAPI server
Write-Host "Starting WebHealthIQ Backend..."
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
