# FareGlitch HubSpot Landing Page Sections

## How to Use These HTML Sections in HubSpot

### Method 1: Using Rich Text Modules (Easiest)

1. **Go to HubSpot Pages**
   - Navigate to: Marketing → Website → Website Pages
   - Click "Create" → "Landing Page"
   - Choose any basic template to start

2. **Add Rich Text Modules**
   - In the page editor, click "Add" (+) button
   - Select "Rich text" module
   - Switch to "Source code" view (<> icon)
   - Copy and paste ONE section at a time from the files below

3. **Section Order** (from top to bottom):
   - `01-hero-section.html` - Hero with headline and plane background
   - `02-stats-section.html` - Three stat boxes ($200+, 60 Min, 500+)
   - `03-how-it-works.html` - Four-step process with emojis
   - `04-recent-deals.html` - Three expired deal examples
   - `05-pricing-section.html` - $5/month pricing card
   - `06-subscribe-cta.html` - Final call-to-action with form

4. **Add Your HubSpot Form**
   - In sections marked "Add your HubSpot form here"
   - Delete the placeholder form HTML
   - Click "Add" → "Form" module
   - Select or create your phone number collection form

### Method 2: Create Custom HTML Module

1. **Go to Design Manager**
   - Navigate to: Marketing → Files and Templates → Design Tools
   - Click "File" → "New file" → "Module"
   - Name it "FareGlitch Section"
   - Paste the section HTML
   - Save and publish

2. **Use in Pages**
   - Go to your landing page editor
   - Click "Add" → find your custom module
   - Drag and drop onto page

### Important Notes

- **Dark Background**: All sections have dark backgrounds (#0f172a, #1e293b)
- **Glassmorphism**: Uses backdrop-filter for blur effects (may not work in all browsers)
- **Responsive**: Grid layouts automatically adjust for mobile
- **Forms**: Replace placeholder forms with actual HubSpot form modules
- **Order Matters**: Stack sections in the numbered order for best visual flow

### Color Scheme

- Primary gradient: #667eea → #764ba2 (purple)
- Accent gradient: #f093fb → #f5576c (pink)
- Dark background: #0f172a
- Card background: rgba(30, 41, 59, 0.5)
- Text primary: #f1f5f9
- Text secondary: #cbd5e1

### Customization Tips

1. **Change Colors**: Search and replace the hex colors
2. **Update Stats**: Edit the numbers in `02-stats-section.html`
3. **Modify Deals**: Update prices and routes in `04-recent-deals.html`
4. **Adjust Pricing**: Change $5 to your actual price in `05-pricing-section.html`
5. **Add More Steps**: Copy/paste a step block in `03-how-it-works.html`

### Testing

1. Preview on desktop and mobile
2. Test all form submissions
3. Check that gradients display correctly
4. Verify glassmorphism effects (may need fallback for older browsers)

### Need Help?

If sections don't display correctly:
- Make sure you're in "Source code" view when pasting
- Check that all `<div>` tags are properly closed
- Try adding one section at a time
- Clear cache and refresh page
