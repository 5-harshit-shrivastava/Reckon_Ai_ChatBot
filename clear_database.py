#!/usr/bin/env python3
"""
Script to clear all data from the Reckon ChatBot database
"""
import sqlite3
import sys
import os

def clear_database():
    """Clear all data from the SQLite database"""

    # Database file path
    db_path = "backend/reckon_chatbot.db"

    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return True

        print(f"Found {len(tables)} tables in the database:")
        for table in tables:
            print(f"  - {table[0]}")

        # Confirm before clearing
        print("\nThis will delete ALL data from ALL tables!")
        confirm = input("Are you sure you want to proceed? (yes/no): ").lower().strip()

        if confirm != 'yes':
            print("Operation cancelled.")
            return False

        # Disable foreign key constraints temporarily
        cursor.execute("PRAGMA foreign_keys = OFF;")

        # Clear all tables
        cleared_tables = []
        for table_name in [t[0] for t in tables]:
            try:
                # Get row count before deletion
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                # Delete all rows from the table
                cursor.execute(f"DELETE FROM {table_name}")
                cleared_tables.append((table_name, row_count))

                print(f"✓ Cleared {row_count} rows from table: {table_name}")
            except sqlite3.Error as e:
                print(f"✗ Error clearing table {table_name}: {e}")

        # Reset auto-increment counters
        for table_name, _ in cleared_tables:
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

        print(f"\n✅ Successfully cleared {len(cleared_tables)} tables from the database!")
        print("Database has been reset to empty state.")

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

def show_database_info():
    """Show information about the database"""

    db_path = "backend/reckon_chatbot.db"

    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names and row counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("Database is empty (no tables).")
            return

        print(f"Database: {db_path}")
        print(f"File size: {os.path.getsize(db_path)} bytes")
        print(f"Tables: {len(tables)}")
        print("\nTable information:")

        total_rows = 0
        for table_name in [t[0] for t in tables]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                print(f"  {table_name}: {row_count} rows")
            except sqlite3.Error as e:
                print(f"  {table_name}: Error - {e}")

        print(f"\nTotal rows across all tables: {total_rows}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Reckon ChatBot Database Cleaner")
    print("=" * 40)

    # Check if database exists
    if not os.path.exists("backend/reckon_chatbot.db"):
        print("❌ Database file not found!")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)

    # Show current database state
    print("Current database state:")
    show_database_info()
    print("\n" + "=" * 40)

    # Clear the database
    if clear_database():
        print("\n" + "=" * 40)
        print("Database state after clearing:")
        show_database_info()
    else:
        print("\n❌ Failed to clear the database!")
        sys.exit(1)