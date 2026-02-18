#!/usr/bin/env python3
"""
HubSpot Website Setup Script

Run this ONCE to set up automatic website updates.
Creates HubDB table and configures integration.
"""
import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

from src.hubspot.website_updater import HubSpotWebsiteUpdater
from src.config import settings

print("="*60)
print("🚀 HUBSPOT WEBSITE AUTO-UPDATE SETUP")
print("="*60)

async def main():
    """Setup HubSpot website integration."""
    
    # Check credentials
    if not settings.hubspot_api_key:
        print("\n❌ ERROR: HUBSPOT_API_KEY not set in .env")
        print("Get your key from: HubSpot → Settings → Integrations → Private Apps")
        sys.exit(1)
        
    print(f"\n✅ HubSpot API Key: {settings.hubspot_api_key[:20]}...")
    
    updater = HubSpotWebsiteUpdater()
    
    print("\n" + "="*60)
    print("STEP 1: Create HubDB Table")
    print("="*60)
    
    print("\n📋 This creates a database table in HubSpot to store deals")
    print("   The table will be used to display deals on your website")
    
    confirm = input("\nCreate HubDB table? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        try:
            table_id = updater.setup_hubdb_table()
            
            print(f"\n✅ SUCCESS! Table created with ID: {table_id}")
            print("\n" + "="*60)
            print("⚠️  IMPORTANT: Add this to your .env file:")
            print("="*60)
            print(f"HUBSPOT_DEALS_TABLE_ID={table_id}")
            print("="*60)
            
            print("\n📝 Next Steps:")
            print("   1. Copy the line above to your .env file")
            print("   2. Add the Recent Deals module to your HubSpot page")
            print("   3. Run your scanner - deals will auto-update!")
            
        except Exception as e:
            print(f"\n❌ Error creating table: {e}")
            sys.exit(1)
    else:
        print("\n⏭️  Skipped table creation")
        
    print("\n" + "="*60)
    print("STEP 2: Add Website Module")
    print("="*60)
    
    print("\n📄 To display deals on your HubSpot website:")
    print("\n   METHOD 1: Using HubDB Module (Recommended)")
    print("   ----------------------------------------")
    print("   1. Go to your HubSpot page editor")
    print("   2. Click 'Add' → Search for 'HubDB'")
    print("   3. Select 'HubDB table' module")
    print("   4. Choose table: 'FareGlitch Deals'")
    print("   5. Customize display template")
    print()
    print("   METHOD 2: Using Custom Module")
    print("   ------------------------------")
    print("   1. Design Manager → Create new module")
    print("   2. Add HubL code to fetch from HubDB:")
    print()
    print("   {% set deals = hubdb_table_rows(YOUR_TABLE_ID) %}")
    print("   {% for row in deals %}")
    print("     <div class='deal'>")
    print("       <h3>{{ row.route }}</h3>")
    print("       <p>Was: ${{ row.normal_price }}</p>")
    print("       <p>Now: ${{ row.deal_price }}</p>")
    print("       <p>Save: ${{ row.savings }}</p>")
    print("     </div>")
    print("   {% endfor %}")
    print()
    print("   METHOD 3: Using API")
    print("   -------------------")
    print("   Create custom JS that fetches from:")
    print(f"   https://api.hubapi.com/cms/v3/hubdb/tables/{table_id if 'table_id' in locals() else 'YOUR_TABLE_ID'}/rows")
    
    print("\n" + "="*60)
    print("STEP 3: Test Integration")
    print("="*60)
    
    print("\n🧪 To test the integration:")
    print("   python test_website_update.py")
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\n🎯 Your scanner will now automatically:")
    print("   1. Send SMS to subscribers")
    print("   2. Update HubDB table with new deals")
    print("   3. Create blog posts (optional)")
    print("   4. Your website displays updated deals!")
    
    print("\n📚 Documentation:")
    print("   - HubDB guide: docs/HUBSPOT_WEBSITE_AUTO_UPDATE.md")
    print("   - Code: src/hubspot/website_updater.py")


if __name__ == "__main__":
    asyncio.run(main())
