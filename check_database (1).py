import sqlite3
import os

print("=" * 50)
print("🧪 SQLite Persistence Test")
print("=" * 50)

# Check if database file exists
db_file = "localwave.db"

if os.path.exists(db_file):
    print(f"\n✅ Database file '{db_file}' EXISTS on disk")
    
    # Show file size
    file_size = os.path.getsize(db_file)
    print(f"📁 File size: {file_size} bytes")
    
    # Connect and show data
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM bands")
    band_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM donations")
    donation_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM events")
    event_count = cursor.fetchone()[0]
    
    print(f"\n📊 Current Data in Database:")
    print(f"   Bands: {band_count}")
    print(f"   Donations: {donation_count}")
    print(f"   Events: {event_count}")
    
    # Show all donations
    if donation_count > 0:
        cursor.execute("""
        SELECT bands.name, donations.amount, donations.date
        FROM donations
        JOIN bands ON donations.band_id = bands.id
        ORDER BY donations.date DESC
        """)
        donations = cursor.fetchall()
        
        print(f"\n💰 All Donations (Total: {donation_count}):")
        for d in donations:
            print(f"   - {d[0]}: £{d[1]} on {d[2]}")
    
    # Show current funding status
    cursor.execute("SELECT name, current_amount, funding_goal FROM bands")
    bands = cursor.fetchall()
    
    print(f"\n🎤 Band Funding Status:")
    for b in bands:
        percentage = (b[1] / b[2]) * 100
        print(f"   - {b[0]}: £{b[1]}/{b[2]} ({percentage:.1f}%)")
    
    conn.close()
    
else:
    print(f"\n❌ Database file '{db_file}' does NOT exist yet")
    print("   Run localwave_final.py first to create it!")

print("\n" + "=" * 50)
print("🔍 Where is the file located?")
print(f"📂 Current directory: {os.getcwd()}")
print(f"📁 Database path: {os.path.abspath(db_file)}")
print("=" * 50)
