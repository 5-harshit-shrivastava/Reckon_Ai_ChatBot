#!/bin/bash

# Start the Reckon ChatBot Frontend
echo "Starting Reckon ChatBot Frontend..."

# Function to start a frontend
start_frontend() {
    local frontend_name=$1
    local frontend_path="frontend/$frontend_name"

    if [ -d "$frontend_path" ]; then
        echo "Starting $frontend_name frontend..."
        cd "$frontend_path"

        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            echo "Installing npm dependencies for $frontend_name..."
            npm install
        fi

        # Start the development server
        npm start &
        echo "$frontend_name frontend started in background"
        cd ../..
    else
        echo "Frontend directory $frontend_path not found"
    fi
}

# Start both frontends
if [ "$1" = "user" ]; then
    start_frontend "user"
elif [ "$1" = "admin" ]; then
    start_frontend "admin"
else
    echo "Starting both user and admin frontends..."
    start_frontend "user"
    sleep 2
    start_frontend "admin"

    echo ""
    echo "Frontends started:"
    echo "- User Frontend: http://localhost:3000"
    echo "- Admin Frontend: http://localhost:3001"
    echo ""
    echo "Backend should be running on: http://localhost:8000"
    echo ""
    echo "To stop the frontends, press Ctrl+C"

    # Wait for user input to stop
    wait
fi