#!/bin/bash
echo ""
echo "======================================"
echo "  SQL Injection Demo — Starting Up"
echo "======================================"
echo ""

# Step 1: Init DB
echo "[1/3] Initializing database..."
python database/init_db.py

echo ""
echo "[2/3] Starting Flask app on http://localhost:5000 ..."
cd flask_app && python app.py &
FLASK_PID=$!
cd ..

sleep 2

echo ""
echo "[3/3] Starting Streamlit on http://localhost:8501 ..."
streamlit run "/home/dev/Documents/sql-injection-demo/streamlit_app/dashboard.py" --server.headless true &
STREAMLIT_PID=$!

echo ""
echo "======================================"
echo "  Flask    → http://localhost:5000"
echo "  Streamlit → http://localhost:8501"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop both servers."
echo ""

# Keep alive and cleanup on exit
trap "kill $FLASK_PID $STREAMLIT_PID 2>/dev/null; echo 'Servers stopped.'" INT TERM
wait
