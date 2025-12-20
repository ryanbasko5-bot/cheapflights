#!/bin/bash
# Quick launch script - Run this to get your next deal!

echo "🚀 FAREGLITCH - FINDING YOUR NEXT DEAL"
echo "======================================"
echo ""

cd /workspaces/cheapflights

# Find deal and send SMS
python find_deals.py

echo ""
echo "======================================"
echo "✅ DONE!"
echo ""
echo "📱 Check your phone for SMS"
echo "📸 Copy Instagram caption above"
echo "🚀 Post to Instagram now!"
echo ""
echo "💰 To add subscriber after payment:"
echo "python scripts/add_subscriber.py +61412345678 monthly"
