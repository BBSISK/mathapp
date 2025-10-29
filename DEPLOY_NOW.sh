#!/bin/bash

echo "🚀 CLASS MONITOR - FINAL DEPLOYMENT"
echo "===================================="
echo ""

# Check if templates directory exists
if [ ! -d "templates" ]; then
    echo "❌ Error: templates/ directory not found"
    echo "   Run this script from your project root directory"
    exit 1
fi

echo "📦 Step 1: Backup existing files..."
if [ -f "templates/class_monitor.html" ]; then
    cp templates/class_monitor.html templates/class_monitor_backup_$(date +%Y%m%d_%H%M%S).html
    echo "✅ Backed up old template"
else
    echo "ℹ️  No existing template to backup"
fi

echo ""
echo "🗑️  Step 2: Remove old template..."
rm -f templates/class_monitor.html
echo "✅ Old template removed"

echo ""
echo "📥 Step 3: Deploy NEW template (1179 lines, NO Tailwind)..."
cp /mnt/user-data/outputs/class_monitor_FINAL.html templates/class_monitor.html
echo "✅ New template deployed"

echo ""
echo "🔍 Step 4: Verify deployment..."
if [ -f "templates/class_monitor.html" ]; then
    FILE_SIZE=$(ls -lh templates/class_monitor.html | awk '{print $5}')
    LINE_COUNT=$(wc -l < templates/class_monitor.html)
    
    echo "✅ File exists: templates/class_monitor.html"
    echo "   Size: $FILE_SIZE"
    echo "   Lines: $LINE_COUNT"
    
    # Check for Tailwind (should return nothing)
    if grep -qi "tailwind" templates/class_monitor.html; then
        echo "⚠️  WARNING: File still contains Tailwind reference!"
        echo "   This might not be the correct file."
    else
        echo "✅ No Tailwind CSS detected (correct!)"
    fi
    
    echo ""
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Restart Flask: python app.py"
    echo "   2. Open browser"
    echo "   3. Press Ctrl+Shift+Delete to clear cache"
    echo "   4. Navigate to Class Monitor"
    echo "   5. Press Ctrl+F5 to hard refresh"
    echo ""
    echo "🎉 The purple gradient should now be GONE!"
    
else
    echo "❌ ERROR: Deployment failed"
    echo "   File not found: templates/class_monitor.html"
    exit 1
fi

echo ""
echo "===================================="
