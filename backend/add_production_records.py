#!/usr/bin/env python3
"""
Add comprehensive production-ready test records for ReckonSales RAG system
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def add_comprehensive_documents():
    """Add comprehensive ReckonSales documentation"""
    try:
        from config.database import get_db
        from models.knowledge_base import Document, DocumentChunk

        print("📚 Adding comprehensive ReckonSales documentation...")

        # Production-ready documents covering all ReckonSales features
        documents = [
            {
                "title": "ReckonSales Inventory Management Complete Guide",
                "content": """ReckonSales provides comprehensive inventory management for businesses of all sizes.

Key Features:
1. Product Management: Add products with SKU, barcode, pricing, and category
2. Stock Tracking: Real-time stock levels with automatic alerts for low stock
3. Purchase Orders: Create and manage supplier orders with delivery tracking
4. Stock Adjustments: Handle damaged goods, returns, and manual adjustments
5. Multi-location Support: Manage inventory across multiple warehouses or stores
6. Barcode Integration: Scan barcodes for quick product identification and updates

Getting Started:
- Navigate to Inventory → Products to add new items
- Set up stock alerts in Settings → Inventory Settings
- Configure suppliers in Masters → Suppliers
- Use Reports → Inventory Reports for detailed analysis

The system automatically updates stock levels when sales or purchases are recorded. You can also set reorder points to get automatic notifications when stock runs low.""",
                "document_type": "user_guide",
                "industry_type": "general",
                "language": "en"
            },

            {
                "title": "ReckonSales में GST और बिलिंग की संपूर्ण गाइड",
                "content": """ReckonSales में GST और बिलिंग की सुविधा बहुत आसान और comprehensive है।

मुख्य सुविधाएं:
1. GST Calculation: Automatic GST calculation सभी items के लिए
2. Invoice Generation: Professional invoices with company logo और details
3. GST Returns: GSTR-1, GSTR-3B reports automatic generation
4. Tax Categories: Different GST rates (0%, 5%, 12%, 18%, 28%) के लिए setup
5. Customer Management: Customer GST numbers और billing addresses
6. Payment Tracking: Due amounts, received payments, और outstanding balance

बिलिंग Process:
- Sales → Create Invoice पर जाएं
- Customer select करें या नया customer add करें
- Products add करें - GST automatically calculate होगा
- Payment details डालें और invoice generate करें
- SMS/Email से invoice send कर सकते हैं

GST Reports:
- Reports → GST Reports में सभी tax reports available हैं
- Monthly/quarterly returns easy export कर सकते हैं
- Tax liability और input credit की automatic calculation""",
                "document_type": "user_guide",
                "industry_type": "general",
                "language": "hi"
            },

            {
                "title": "ReckonSales Pharmacy Management Features",
                "content": """ReckonSales offers specialized pharmacy management features to meet healthcare industry requirements.

Pharmacy-Specific Features:
1. Medicine Master Data: Store detailed drug information including generic names, brands, compositions
2. Batch Management: Track batch numbers, manufacturing dates, and expiry dates
3. Expiry Alerts: Automatic notifications for medicines nearing expiry
4. Drug Interaction Warnings: Alert system for potentially harmful drug combinations
5. Prescription Management: Digital prescription storage and tracking
6. Patient Records: Maintain customer health profiles and purchase history
7. Regulatory Compliance: Generate reports for drug control authorities

Setting Up Pharmacy Module:
- Enable Pharmacy mode in Settings → Industry Settings
- Configure medicine categories in Masters → Drug Categories
- Set up suppliers with drug licenses in Masters → Suppliers
- Configure expiry alert periods in Settings → Alerts

Prescription Process:
- Create customer profile with patient details
- Scan or enter prescription details
- Add medicines with batch verification
- System checks for interactions and allergies
- Generate medicine bill with patient counseling notes

The system maintains complete audit trails for regulatory compliance and supports various report formats required by pharmaceutical boards.""",
                "document_type": "user_guide",
                "industry_type": "pharmacy",
                "language": "en"
            },

            {
                "title": "ReckonSales Auto Parts Management System",
                "content": """ReckonSales provides specialized features for auto parts businesses to manage vehicle-specific inventory and compatibility.

Auto Parts Features:
1. Vehicle Database: Comprehensive vehicle make, model, year database
2. Parts Compatibility: Link parts to specific vehicle models
3. OEM vs Aftermarket: Classify parts as original or aftermarket
4. Cross-Reference: Alternative part numbers and compatibility mapping
5. Technical Specifications: Store detailed part specifications and fitment data
6. Catalog Management: Digital parts catalogs with images and descriptions
7. Core Exchange: Handle returnable cores and exchange processes

Setting Up Auto Parts Module:
- Enable Auto Parts mode in Settings → Industry Settings
- Import vehicle database from Masters → Vehicle Database
- Set up part categories in Masters → Parts Categories
- Configure suppliers with part compatibility data

Parts Search and Selection:
- Search by vehicle: Enter make, model, year to find compatible parts
- Search by part number: Direct part number lookup with alternatives
- VIN decoder: Enter VIN to get exact vehicle specifications
- Interchange lookup: Find alternative parts from different manufacturers

Inventory Features:
- Multi-location tracking for different warehouses
- Shelf location mapping for quick parts picking
- Seasonal demand tracking for popular parts
- Warranty tracking for parts with warranty periods""",
                "document_type": "user_guide",
                "industry_type": "auto_parts",
                "language": "en"
            },

            {
                "title": "ReckonSales Customer and CRM Management",
                "content": """ReckonSales includes powerful CRM features to manage customer relationships and drive business growth.

Customer Management Features:
1. Customer Profiles: Complete customer information including contact details, preferences
2. Purchase History: Track all transactions and buying patterns
3. Credit Management: Set credit limits and track outstanding balances
4. Customer Categories: Segment customers into groups for targeted marketing
5. Communication Log: Track all interactions, calls, and emails
6. Loyalty Programs: Points-based loyalty and rewards system
7. Customer Statements: Generate detailed account statements

CRM Capabilities:
- Lead Management: Track prospects from inquiry to conversion
- Follow-up Reminders: Automated reminders for customer follow-ups
- Sales Analytics: Customer lifetime value, purchase frequency analysis
- Marketing Campaigns: Email and SMS marketing with customer segmentation
- Customer Support: Ticket system for handling customer queries

Setting Up Customer Management:
- Configure customer categories in Masters → Customer Categories
- Set up loyalty program rules in Settings → Loyalty Settings
- Create customer groups for marketing in Marketing → Customer Groups
- Set credit terms and limits in Settings → Credit Management

Best Practices:
- Regular customer data cleanup and validation
- Segment customers based on purchase behavior
- Use automated follow-ups for better customer retention
- Track customer feedback and satisfaction scores
- Integrate with external marketing tools for better reach""",
                "document_type": "user_guide",
                "industry_type": "general",
                "language": "en"
            },

            {
                "title": "ReckonSales Reports and Analytics Dashboard",
                "content": """ReckonSales provides comprehensive reporting and analytics to help you make data-driven business decisions.

Report Categories:
1. Sales Reports: Daily, monthly, yearly sales analysis with trends
2. Inventory Reports: Stock levels, movement, aging, and reorder reports
3. Financial Reports: Profit/Loss, Balance Sheet, Cash Flow statements
4. Tax Reports: GST returns, tax liability, input credit reports
5. Customer Reports: Customer aging, payment history, loyalty analysis
6. Supplier Reports: Purchase analysis, payment due, supplier performance

Dashboard Features:
- Real-time business metrics and KPIs
- Interactive charts and graphs
- Customizable widgets and layout
- Alert notifications for important events
- Mobile-responsive design for anywhere access

Key Performance Indicators:
- Daily/Monthly sales targets vs actual
- Inventory turnover ratios
- Customer acquisition and retention rates
- Profit margins by product and category
- Cash flow and working capital analysis
- Top selling products and customers

Generating Reports:
- Navigate to Reports section from main menu
- Select report category and specific report type
- Choose date range and filter criteria
- Customize columns and sorting options
- Export to Excel, PDF, or print directly

Advanced Analytics:
- Sales forecasting based on historical data
- Seasonal trend analysis
- ABC analysis for inventory optimization
- Customer lifetime value calculations
- Supplier performance scorecards""",
                "document_type": "user_guide",
                "industry_type": "general",
                "language": "en"
            },

            {
                "title": "ReckonSales System Setup and Configuration",
                "content": """Complete guide for setting up ReckonSales system for your business requirements.

Initial Setup Steps:
1. Company Information: Add company details, logo, address, and tax numbers
2. User Management: Create user accounts with appropriate access permissions
3. Industry Configuration: Select and configure industry-specific features
4. Masters Setup: Add customers, suppliers, products, and categories
5. Tax Configuration: Set up GST rates, tax categories, and compliance settings
6. Banking Setup: Configure bank accounts and payment methods
7. Backup Configuration: Set up automatic data backup schedules

Configuration Modules:
- General Settings: Basic system preferences and defaults
- Inventory Settings: Stock management rules and reorder points
- Accounting Settings: Chart of accounts and financial year setup
- User Permissions: Role-based access control for different users
- Integration Settings: Connect with external systems and APIs
- Security Settings: Password policies and session timeouts

Best Practices for Setup:
- Start with master data - customers, suppliers, products
- Configure tax settings according to your business location
- Set appropriate user roles and permissions for security
- Test all configurations with sample transactions
- Train users on the system before going live
- Set up regular data backup and recovery procedures

Maintenance Tasks:
- Regular data cleanup and archival
- User access review and updates
- System performance monitoring
- Software updates and patches
- Data backup verification
- Security audit and compliance checks

The system is designed to grow with your business - you can add features and modules as needed.""",
                "document_type": "user_guide",
                "industry_type": "general",
                "language": "en"
            }
        ]

        # Get database session
        db = next(get_db())

        # Clear existing test documents to avoid duplicates
        existing_docs = db.query(Document).filter(
            Document.file_path.like('/production/%')
        ).all()

        if existing_docs:
            print(f"  🗑️ Removing {len(existing_docs)} existing production documents...")
            for doc in existing_docs:
                db.delete(doc)
            db.commit()

        documents_added = 0
        chunks_added = 0

        for i, doc_data in enumerate(documents, 1):
            # Create document
            document = Document(
                title=doc_data["title"],
                content=doc_data["content"],
                document_type=doc_data["document_type"],
                industry_type=doc_data["industry_type"],
                language=doc_data["language"],
                file_path=f"/production/doc_{i}.txt",
                file_size=len(doc_data["content"])
            )

            db.add(document)
            db.flush()

            # Split content into chunks (optimal size for embeddings)
            content = doc_data["content"]
            chunk_size = 400  # Optimal for Google EmbeddingGemma
            overlap = 50      # Small overlap for better context

            chunks = []
            start = 0
            chunk_index = 0

            while start < len(content):
                end = start + chunk_size
                chunk_text = content[start:end]

                # Try to break at sentence boundary
                if end < len(content):
                    last_period = chunk_text.rfind('.')
                    last_newline = chunk_text.rfind('\n')
                    break_point = max(last_period, last_newline)

                    if break_point > start + 200:  # Minimum chunk size
                        chunk_text = content[start:start + break_point + 1]
                        end = start + break_point + 1

                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=chunk_index,
                    chunk_text=chunk_text.strip(),
                    chunk_size=len(chunk_text),
                    overlap_with_previous=overlap if chunk_index > 0 else 0,
                    section_title=doc_data["title"],
                    keywords=f"reckon, {doc_data['industry_type']}, {doc_data['document_type']}, {doc_data['language']}",
                    confidence_score=0.85,
                    embedding_created=False
                )

                chunks.append(chunk)
                chunks_added += 1
                chunk_index += 1

                # Move start position with overlap
                start = end - overlap if end < len(content) else len(content)

            db.add_all(chunks)
            documents_added += 1
            print(f"  ✅ Added: {doc_data['title'][:50]}... ({len(chunks)} chunks)")

        db.commit()
        db.close()

        print(f"\n🎉 Successfully added {documents_added} production documents!")
        print(f"📝 Total chunks created: {chunks_added}")
        return True

    except Exception as e:
        print(f"❌ Error adding documents: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_database_summary():
    """Show current database status"""
    try:
        from config.database import get_db
        from models.knowledge_base import Document, DocumentChunk

        print("\n📊 Database Summary:")

        db = next(get_db())

        # Get counts
        total_docs = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        embedded_chunks = db.query(DocumentChunk).filter(DocumentChunk.embedding_created == True).count()

        print(f"  📄 Total Documents: {total_docs}")
        print(f"  📝 Total Chunks: {total_chunks}")
        print(f"  🔗 Embedded Chunks: {embedded_chunks}")

        # Show by language
        en_docs = db.query(Document).filter(Document.language == 'en').count()
        hi_docs = db.query(Document).filter(Document.language == 'hi').count()

        print(f"\n🌐 By Language:")
        print(f"  🇺🇸 English: {en_docs} documents")
        print(f"  🇮🇳 Hindi: {hi_docs} documents")

        # Show by industry
        industries = db.query(Document.industry_type).distinct().all()
        print(f"\n🏭 By Industry:")
        for (industry,) in industries:
            count = db.query(Document).filter(Document.industry_type == industry).count()
            print(f"  • {industry}: {count} documents")

        db.close()

    except Exception as e:
        print(f"❌ Database summary error: {e}")

def main():
    """Main function"""
    print("🚀 Adding Production-Ready ReckonSales Documentation")
    print("=" * 60)

    # Add comprehensive documents
    if add_comprehensive_documents():
        # Show database summary
        show_database_summary()

        print("\n" + "=" * 60)
        print("✅ Production documentation added successfully!")
        print("\n📋 What's Ready:")
        print("  • Comprehensive ReckonSales feature documentation")
        print("  • Hindi/English multilingual content")
        print("  • Industry-specific guides (pharmacy, auto parts)")
        print("  • Optimized chunks for Google EmbeddingGemma")
        print("  • Ready for embedding generation")

        print("\n🔧 Next Steps:")
        print("  1. Embeddings will be created when EmbeddingGemma is ready")
        print("  2. Test RAG queries with comprehensive content")
        print("  3. Your knowledge base is production-ready!")

    else:
        print("❌ Failed to add production documentation")

if __name__ == "__main__":
    main()