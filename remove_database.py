#!/usr/bin/env python3
"""
Script to completely remove the database file
"""
import os

def remove_database():
    """Remove the database file completely"""

    db_path = "backend/reckon_chatbot.db"

    if not os.path.exists(db_path):
        print("✅ Database file doesn't exist - nothing to remove.")
        return True

    try:
        # Get file size before removal
        file_size = os.path.getsize(db_path)

        # Remove the file
        os.remove(db_path)

        print(f"✅ Database file removed successfully!")
        print(f"   File size: {file_size} bytes")
        print("   The database will be recreated when the backend starts next time.")

        return True

    except Exception as e:
        print(f"❌ Error removing database file: {e}")
        return False

if __name__ == "__main__":
    print("Reckon ChatBot Database Remover")
    print("=" * 40)

    if not os.path.exists("backend"):
        print("❌ Backend directory not found!")
        print("Make sure you're running this from the project root directory.")
        exit(1)

    success = remove_database()

    if not success:
        exit(1)