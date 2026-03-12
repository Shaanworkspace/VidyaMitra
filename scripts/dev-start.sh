#!/bin/bash
# Development Environment Startup Script

echo "🚀 Starting VidyaMitra Career Agent Development Environment"

# Start backend
echo "Starting backend on port 8000..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on port 3000..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Trap to cleanup processes on exit
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

echo "✅ Development servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user interrupt
wait