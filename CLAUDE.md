# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sistema Seja Sua** - A comprehensive clothing store management system built with Django and PostgreSQL.

This is a web-only (desktop) application for managing all aspects of a clothing business including inventory, collections, finance, calendar, statistics, marketing, and business settings.

## Technology Stack

- **Backend:** Django 5.0
- **Database:** PostgreSQL
- **Frontend:** Django Templates (HTML, CSS, JavaScript)
- **Image Storage:** Django local storage
- **APIs:** Google Calendar API, Tiny ERP API
- **Data Analysis:** NumPy, Pandas, SciPy (for sales forecasting)

## Development Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Create database (ensure PostgreSQL is running)
createdb store_management_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Project Structure

### Django Apps

- `business_settings/` - Suppliers, Piece Categories, Business Deadlines
- `store_collections/` - Collections, Pieces, Fabrics, Accessories
- `inventory/` - Inventory management with Tiny ERP API integration
- `calendar_app/` - Google Calendar integration for production timelines
- `finance/` - Financial tracking, forecasting, cash flow
- `sales_stats/` - Sales projections and statistics
- `notes/` - Note-taking with autosave functionality
- `marketing/` - Marketing campaigns and activities

### Key Models

**business_settings:**
- `Supplier` - Fabric and accessory suppliers with delivery times
- `PieceCategory` - Categories and subcategories for clothing pieces
- `BusinessDeadlines` - Default production timeline deadlines (singleton pattern)

**store_collections:**
- `Collection` - Clothing collections with status tracking and launch dates
- `Piece` - Individual pieces with pricing, cost calculation, sizes (P,M,G,GG)
- `Fabric` - Fabric materials with supplier, weight, and yield information
- `Accessory` - Accessories used in pieces
- `PieceColor` - Color variants for pieces with hex codes
- `PieceImage` - Modeling images uploadable after piece creation

**inventory:** (Tiny ERP API Integration)
- `InventoryPiece` - Pieces synced from Tiny ERP (read-only)
- `InventoryAccessory` - Manually managed accessories
- `Packaging` - Packaging materials inventory
- `Gift` - Gift items inventory

**finance:** (Tiny ERP API Integration)
- `FinanceSector` - Configurable sectors for expense categorization
- `FinanceInflow` - Money inflows from Tiny ERP (read-only)
- `FinanceOutflow` - Money outflows/expenses from Tiny ERP (read-only)
- `PredictedExpense` - Auto-calculated expense predictions from Statistics

**calendar_app:** (Google Calendar API Integration)
- `CalendarEvent` - Events with Google Calendar sync
  - Event types: modeling, pilot_piece, test_piece, production, preparation, transportation, launch
  - Auto-created from collection save operations
  - Collection milestone events are read-only

**sales_stats:** (Data Science & Tiny ERP API)
- `SalesData` - Historical sales from Tiny ERP (read-only)
- `PieceSalesStatistics` - Aggregated sales stats per piece
- `CollectionSalesStatistics` - Aggregated stats per collection
- `FabricSalesStatistics` - Usage and sales stats per fabric
- `SalesForecast` - Predictions using NumPy/Pandas/SciPy

**marketing:**
- `MarketingCampaign` - Campaigns with budgets and date ranges
- `SocialMediaPost` - Social media scheduling and engagement tracking
- `PromotionalMaterial` - Marketing assets and materials

**notes:**
- `Note` - Notes with title, content, and autosave functionality

## Database

PostgreSQL database with ISO 8601 date formats and decimal values for financial data.

Configure connection in `.env`:
```
DB_NAME=store_management_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Common Commands

```bash
# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Admin
python manage.py createsuperuser
python manage.py changepassword <username>

# Development server
python manage.py runserver
python manage.py runserver 0.0.0.0:8000

# Shell
python manage.py shell
python manage.py dbshell

# Static files
python manage.py collectstatic

# Testing
python manage.py test
python manage.py test <app_name>
```

## Frontend Structure

### Templates
- `templates/base.html` - Base template with beige background and left-side navigation
- `templates/home.html` - Dashboard home page with module cards

### Static Files
- `static/css/style.css` - Main stylesheet with beige color scheme
  - Variables: --beige-light, --beige-medium, --beige-dark, --brown-text, --accent-gold
  - Responsive card-based layout
  - Custom sidebar navigation styling
- `static/js/main.js` - JavaScript utilities
  - Auto-save for notes
  - Navigation highlighting
  - Currency/date formatting utilities (pt-BR)

### Navigation Structure
Left-side menu with sections:
- Página Inicial (Home)
- Coleções (Collections, Pieces, Fabrics)
- Estoque (Inventory, Accessories)
- Financeiro (Inflows, Outflows, Predictions)
- Calendário (Events)
- Estatísticas (Sales Data, Forecasts)
- Marketing (Campaigns, Social Media)
- Anotações (Notes)
- Configurações (Settings, Django Admin)

## Application Features

### Collections Module
- Create collections with multiple pieces
- Define fabric consumption per size (P, M, G, GG)
- Track initial quantities per size
- Upload modeling images (only after piece creation)
- Calculate margins: (sale_price - cost) / sale_price
- Manage colors and accessories
- Status tracking: awaiting_modeler → awaiting_pilot → awaiting_production → released

### Inventory Module
- Sync pieces from Tiny ERP API (read-only)
- Manage accessories, packaging, and gifts manually
- Track minimum quantities and delivery times
- Price tracking for all inventory items

### Finance Module
- Track money inflows from Tiny ERP (read-only)
- Track expenses/outflows from Tiny ERP (read-only)
- Configurable finance sectors for categorization
- Predicted expenses calculated from Statistics module
- Confidence levels for predictions

### Calendar Module
- Automatic event creation based on collection deadlines
- Backward calculation from launch date
- Event dependencies: transportation → preparation → production → test piece → pilot piece → modeling
- Special handling for new fabrics (adds fabric testing phase)
- Google Calendar API integration for two-way sync
- Collection milestone events are read-only

### Statistics Module
- Sales data sync from Tiny ERP API
- Aggregated statistics per piece, collection, and fabric
- Sales forecasting using NumPy, Pandas, SciPy
- Confidence intervals for predictions
- Track best/worst selling pieces per collection
- Size-specific sales tracking (P, M, G, GG)

### Marketing Module
- Campaign management with budgets and timelines
- Social media post scheduling (Instagram, Facebook, TikTok, etc.)
- Engagement metrics tracking (likes, comments, shares, views)
- Promotional materials library
- Link campaigns to collections and pieces

### Business Settings
- Configure suppliers with delivery times
- Define piece categories and subcategories
- Set default production deadlines (modeling, pilot piece, production, etc.)
- Singleton BusinessDeadlines prevents multiple configurations

### Notes Module
- Quick note-taking with autosave functionality
- JavaScript auto-save every 2 seconds after typing stops
- User attribution for notes

## Notes

- The application uses Portuguese (pt-BR) locale and São Paulo timezone
- Desktop-only interface (no mobile responsiveness)
- Beige background color scheme
- Left-side menu navigation
- All sectors visible in menu even when empty
- Collection save triggers automatic updates to Statistics, Finance, and Calendar modules

## Development Workflow

1. Always activate virtual environment before working
2. Pull latest changes before starting work
3. Create migrations after model changes
4. Test changes locally before committing
5. Use Django admin for testing data models
6. Follow Django best practices for views and templates

## API Integrations

### Google Calendar API
- OAuth 2.0 authentication
- Credentials stored in environment variables
- Used for production timeline management

### Tiny ERP API
- JSON format for data exchange
- Provides inventory pieces data
- Provides financial inflow/outflow data
- Read-only integration (no manual editing of API data)

## Important Constraints

- Pieces cannot be edited after creation (except modeling images)
- Business Deadlines should have only one instance (singleton pattern)
- Collection deadlines can override business defaults
- New fabrics trigger additional "fabric testing" calendar events
- All financial data uses decimal precision (DecimalField)
- Dates follow ISO 8601 format
- InventoryPiece, FinanceInflow, FinanceOutflow, SalesData are read-only (API-synced)
- Collection milestone calendar events are read-only (auto-generated)

## Implementation Status

### Completed ✓
1. **Django Project Setup**
   - Django 5.0 with PostgreSQL configuration
   - 8 Django apps created and configured
   - Environment variables with .env file
   - Portuguese locale and São Paulo timezone

2. **Database Models**
   - All 8 modules have complete models
   - Migrations created for all modules
   - Admin interfaces configured for all models
   - Proper foreign key relationships
   - Read-only admin for API-synced models

3. **Admin Interface**
   - Custom admin for each model
   - Inline editing for related models
   - Fieldsets for organized data entry
   - List filters and search functionality
   - Date hierarchy for temporal data
   - Custom permissions (no add/delete for API data)

4. **Frontend Structure**
   - Base template with beige background
   - Left-side navigation menu
   - Home dashboard with module cards
   - Responsive CSS styling
   - JavaScript utilities for auto-save and formatting
   - URL routing configured

### Completed Implementation ✓

5. **Automatic Triggers (Django Signals)**
   - `store_collections/signals.py` - Collection save triggers
   - Auto-create calendar events when collection is saved with launch date
   - Backward date calculation from launch date
   - Auto-update collection and piece statistics
   - Auto-delete calendar events when collection is deleted

6. **Google Calendar API Integration**
   - `calendar_app/google_calendar.py` - Google Calendar service
   - `calendar_app/signals.py` - Auto-sync signals
   - OAuth 2.0 authentication with credentials.json
   - Create, update, delete events in Google Calendar
   - Management command: `python manage.py sync_calendar`
   - All-day and timed event support
   - São Paulo timezone support

7. **Tiny ERP API Integration**
   - `inventory/tiny_erp.py` - Inventory sync service
   - `finance/tiny_erp.py` - Finance sync service
   - `sales_stats/tiny_erp.py` - Sales data sync service
   - Management commands:
     - `python manage.py sync_inventory`
     - `python manage.py sync_finance`
     - `python manage.py sync_sales`
   - JSON parsing for Tiny ERP format
   - Update or create records (no duplicates)
   - Error handling and logging
   - Automatic sector creation for finance data

### Pending Implementation ⏳

1. **Data Science Features**
   - Sales forecasting algorithms (using NumPy/Pandas/SciPy)
   - Statistical analysis for predictions
   - Confidence interval calculations
   - Automatic statistics aggregation from sales data
   - Management command: `python manage.py generate_forecasts`

## Management Commands

### API Synchronization

```bash
# Sync inventory from Tiny ERP
python manage.py sync_inventory
python manage.py sync_inventory --verbose

# Sync finance data from Tiny ERP
python manage.py sync_finance
python manage.py sync_finance --verbose

# Sync sales data from Tiny ERP
python manage.py sync_sales
python manage.py sync_sales --verbose

# Sync calendar events to Google Calendar
python manage.py sync_calendar
python manage.py sync_calendar --all  # Sync all events
python manage.py sync_calendar --verbose
```

### Setup Cron Jobs (Optional)

For automatic daily syncing:

```bash
# Edit crontab
crontab -e

# Add these lines (adjust paths):
0 2 * * * cd /path/to/project && source venv/bin/activate && python manage.py sync_inventory
0 3 * * * cd /path/to/project && source venv/bin/activate && python manage.py sync_finance
0 4 * * * cd /path/to/project && source venv/bin/activate && python manage.py sync_sales
```

## API Setup Instructions

### Google Calendar API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`
6. Place in project root
7. Update `.env`:
   ```
   GOOGLE_CREDENTIALS_PATH=credentials.json
   GOOGLE_CALENDAR_ID=primary
   ```
8. First run will open browser for authorization
9. Token will be saved to `token.json`

### Tiny ERP API Setup

1. Login to [Tiny ERP](https://www.tiny.com.br/)
2. Go to Settings > Integrations > API
3. Copy your API token
4. Update `.env`:
   ```
   TINY_ERP_API_TOKEN=your_token_here
   TINY_ERP_API_URL=https://api.tiny.com.br/api2
   ```

## Next Steps for Development

1. **Implement Sales Forecasting:**
   - Create `sales_stats/forecasting.py` module
   - Implement forecasting algorithms using NumPy/Pandas/SciPy
   - Linear regression, ARIMA, or seasonal decomposition
   - Create management command: `python manage.py generate_forecasts`
   - Auto-calculate confidence intervals
   - Update PredictedExpense based on forecasts

2. **Enhanced Features (Optional):**
   - Email notifications for upcoming events
   - Automated reports generation
   - Dashboard charts and graphs
   - Batch import/export functionality
   - Advanced search and filtering

## Current System Capabilities

The system is **fully functional** for:
- ✅ Creating and managing collections with automatic calendar events
- ✅ Managing pieces with size-specific data (P, M, G, GG)
- ✅ Syncing inventory from Tiny ERP API
- ✅ Syncing finance data from Tiny ERP API
- ✅ Syncing sales data from Tiny ERP API
- ✅ Two-way Google Calendar synchronization
- ✅ Automatic statistics tracking per piece/collection/fabric
- ✅ Marketing campaign management
- ✅ Social media post scheduling
- ✅ Note-taking with auto-save
- ✅ Comprehensive Django admin interface
- ✅ Dashboard home page with module cards

## Quick Start

1. **Install & Setup:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your database credentials
   ```

2. **Database:**
   ```bash
   createdb store_management_db
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. **Run Server:**
   ```bash
   python manage.py runserver
   ```
   - Home: http://localhost:8000/
   - Admin: http://localhost:8000/admin/

4. **Configure APIs (Optional):**
   - Add `credentials.json` for Google Calendar
   - Add Tiny ERP token to `.env`
   - Run sync commands

5. **Start Using:**
   - Configure business settings (suppliers, categories, deadlines)
   - Create your first collection
   - Add pieces to the collection
   - System automatically creates calendar events!
   - Sync with external APIs as needed
