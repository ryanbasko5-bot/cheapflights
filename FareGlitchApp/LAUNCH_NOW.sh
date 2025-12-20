#!/bin/bash

# FareGlitch App Launch Script
# This will build and deploy your app to iOS and Android

set -e

echo "🚀 FareGlitch Mobile App Deployment"
echo "===================================="
echo ""

# Check if EAS CLI is installed
if ! command -v eas &> /dev/null; then
    echo "📦 Installing EAS CLI..."
    npm install -g eas-cli
fi

cd /workspaces/cheapflights/FareGlitchApp

# Login to Expo
echo "🔐 Please login to your Expo account..."
eas login

echo ""
echo "Choose deployment type:"
echo "1) Preview Build (Testing) - APK for Android, Simulator for iOS"
echo "2) Production Build (App Stores) - Submit to Apple App Store & Google Play"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🔨 Building preview versions..."
        echo "This will create:"
        echo "  - Android: APK file you can install directly"
        echo "  - iOS: Simulator build for testing"
        echo ""
        eas build --platform all --profile preview
        echo ""
        echo "✅ Preview builds complete!"
        echo "📲 Download links will appear in your Expo dashboard: https://expo.dev"
        ;;
    2)
        echo ""
        echo "🔨 Building production versions..."
        echo ""
        eas build --platform all --profile production
        
        echo ""
        echo "📤 Submitting to app stores..."
        read -p "Submit to iOS App Store? (y/n): " ios_submit
        if [ "$ios_submit" = "y" ]; then
            echo "🍎 Submitting to Apple App Store..."
            echo "You'll need:"
            echo "  - Apple Developer account"
            echo "  - App-specific password from appleid.apple.com"
            eas submit --platform ios
        fi
        
        read -p "Submit to Google Play Store? (y/n): " android_submit
        if [ "$android_submit" = "y" ]; then
            echo "🤖 Submitting to Google Play Store..."
            echo "You'll need your Google Play Console credentials"
            eas submit --platform android
        fi
        
        echo ""
        echo "✅ Production deployment complete!"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process finished!"
echo "📊 Check build status: https://expo.dev"
echo "📱 Manage your apps:"
echo "   - iOS: https://appstoreconnect.apple.com"
echo "   - Android: https://play.google.com/console"
