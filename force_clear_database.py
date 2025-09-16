#!/usr/bin/env python3
"""
Script to force clear all data from the Reckon ChatBot database (no confirmation)
"""
import sqlite3
import os

def force_clear_database():
    """Force clear all data from the SQLite database without confirmation"""

    # Database file path
    db_path = "backend/reckon_chatbot.db"

    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("✅ Database is already empty (no tables found).")
            return True

        print(f"Found {len(tables)} tables in the database:")

        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF;")

        # Clear all tables
        total_cleared_rows = 0
        for table_name in [t[0] for t in tables]:
            try:
                # Get row count before deletion
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                if row_count > 0:
                    # Delete all rows from the table
                    cursor.execute(f"DELETE FROM {table_name}")
                    total_cleared_rows += row_count
                    print(f"✓ Cleared {row_count} rows from table: {table_name}")
                else:
                    print(f"• Table {table_name} was already empty")

            except sqlite3.Error as e:
                print(f"✗ Error clearing table {table_name}: {e}")

        # Reset auto-increment counters
        for table_name in [t[0] for t in tables]:
            try:
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
            except sqlite3.Error:
                pass  # Table might not have auto-increment

        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Commit changes
        conn.commit()

        # Vacuum to reclaim space
        cursor.execute("VACUUM")

        print(f"\n✅ Database cleared successfully!")
        print(f"   Total rows cleared: {total_cleared_rows}")
        print(f"   Tables processed: {len(tables)}")
        print("   Database has been reset to empty state.")

        return True

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Reckon ChatBot Database Force Clear")
    print("=" * 40)

    # Check if database exists
    if not os.path.exists("backend/reckon_chatbot.db"):
        print("❌ Database file not found!")
        print("Make sure you're running this from the project root directory.")
        exit(1)

    # Show file size before
    db_size_before = os.path.getsize("backend/reckon_chatbot.db")
    print(f"Database file size before: {db_size_before} bytes")

    # Clear the database
    success = force_clear_database()

    if success:
        # Show file size after
        db_size_after = os.path.getsize("backend/reckon_chatbot.db")
        print(f"Database file size after: {db_size_after} bytes")
        print(f"Space reclaimed: {db_size_before - db_size_after} bytes")
    else:
        print("\n❌ Failed to clear the database!")
        exit(1)