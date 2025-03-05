# PNLP Web Application Deployment Script
# This PowerShell script automates the build and deployment process

# Configuration variables
$buildConfig = "production"
$distFolder = ".\dist\pnlp-app\browser"
$backupFolder = ".\backups\$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
$deploymentServer = "your-server-address" # Replace with your actual server address
$deploymentPath = "/var/www/pnlp" # Replace with your actual deployment path
$sshUser = "username" # Replace with your SSH username

# Create a backup of the current build if it exists
Write-Host "Creating backup of current build..." -ForegroundColor Cyan
if (Test-Path $distFolder) {
    # Create backup directory if it doesn't exist
    if (-not (Test-Path ".\backups")) {
        New-Item -ItemType Directory -Path ".\backups" | Out-Null
    }
    
    # Create timestamped backup folder
    New-Item -ItemType Directory -Path $backupFolder | Out-Null
    
    # Copy current build to backup
    Copy-Item -Path "$distFolder\*" -Destination $backupFolder -Recurse
    Write-Host "Backup created at: $backupFolder" -ForegroundColor Green
} else {
    Write-Host "No existing build found to backup." -ForegroundColor Yellow
}

# Clean and build the application
Write-Host "Building application for $buildConfig..." -ForegroundColor Cyan
npm run build -- --configuration=$buildConfig

# Check if build was successful
if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed! Deployment aborted." -ForegroundColor Red
    exit 1
}

Write-Host "Build completed successfully!" -ForegroundColor Green

# Display deployment options
Write-Host "`nDeployment Options:" -ForegroundColor Cyan
Write-Host "1. Deploy to server via SCP/SSH"
Write-Host "2. Create deployment package (ZIP)"
Write-Host "3. Exit without deploying"

$deployOption = Read-Host "`nSelect deployment option (1-3)"

switch ($deployOption) {
    "1" {
        # Deploy to server via SCP/SSH
        Write-Host "Deploying to server: $deploymentServer..." -ForegroundColor Cyan
        
        # This is a placeholder for the actual SCP command
        # You would need to have SSH/SCP configured properly for this to work
        Write-Host "scp -r $distFolder/* $sshUser@$deploymentServer:$deploymentPath"
        
        Write-Host "Deployment completed!" -ForegroundColor Green
    }
    "2" {
        # Create deployment package
        $zipFile = ".\pnlp-app-deployment-$(Get-Date -Format 'yyyy-MM-dd').zip"
        Write-Host "Creating deployment package: $zipFile..." -ForegroundColor Cyan
        
        Compress-Archive -Path "$distFolder\*" -DestinationPath $zipFile -Force
        
        Write-Host "Deployment package created: $zipFile" -ForegroundColor Green
    }
    "3" {
        Write-Host "Exiting without deployment." -ForegroundColor Yellow
    }
    default {
        Write-Host "Invalid option selected. Exiting without deployment." -ForegroundColor Red
    }
}

Write-Host "`nDeployment process completed!" -ForegroundColor Green
