#!/bin/bash
set -e

echo "=== Azure App Service ODBC Configuration ==="

# In Azure App Service, we can't install packages
# Instead, we'll check what's already installed and configure our app

echo "Checking for ODBC drivers..."
if command -v odbcinst >/dev/null 2>&1; then
    echo "ODBC installed, checking for drivers:"
    odbcinst -q -d || echo "No ODBC drivers found"
else
    echo "ODBC not installed"
fi

# Check for SQL Server driver locations
echo "Checking for SQL Server ODBC driver files:"
find /opt -name "*msodbcsql*" 2>/dev/null || echo "No MSSQL ODBC found in /opt"
find /usr -name "*msodbcsql*" 2>/dev/null || echo "No MSSQL ODBC found in /usr"

# Create local odbcinst.ini if it doesn't exist
mkdir -p $HOME/.odbcinst
if [ ! -f "$HOME/.odbcinst/odbcinst.ini" ]; then
    echo "Creating odbcinst.ini in $HOME/.odbcinst"
    cat > $HOME/.odbcinst/odbcinst.ini << EOF
[ODBC Driver 17 for SQL Server]
Description=Microsoft ODBC Driver 17 for SQL Server
Driver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.10.so.4.1
EOF
fi

echo "Setting ODBCSYSINI environment variable"
export ODBCSYSINI=$HOME/.odbcinst

echo "=== ODBC Configuration Complete ==="