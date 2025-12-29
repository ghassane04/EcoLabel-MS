#!/bin/bash
# ===========================================
# EcoLabel-MS - JMeter Test Runner (Linux/Mac)
# ===========================================

echo "========================================"
echo "  EcoLabel-MS - JMeter Load Tests"
echo "========================================"

# Configuration
TEST_PLAN="ecolabel-load-test.jmx"
RESULTS_DIR="jmeter-results"
REPORT_DIR="jmeter-report"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create directories
mkdir -p $RESULTS_DIR
rm -rf $REPORT_DIR

echo ""
echo "[1/3] Starting services..."
docker-compose up -d
sleep 30

echo ""
echo "[2/3] Running JMeter tests..."
jmeter -n -t $TEST_PLAN -l $RESULTS_DIR/results_$TIMESTAMP.jtl -e -o $REPORT_DIR

echo ""
echo "[3/3] Tests completed!"
echo ""
echo "Results: $RESULTS_DIR/results_$TIMESTAMP.jtl"
echo "Report:  $REPORT_DIR/index.html"
echo ""

# Open report (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open $REPORT_DIR/index.html
# Open report (Linux)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open $REPORT_DIR/index.html
fi
