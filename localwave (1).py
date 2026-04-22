import sqlite3
import math
from datetime import datetime

# ---------------- DATABASE ----------------
conn = sqlite3.connect("localwave.db")
cursor = conn.cursor()

# Bands table
cursor.execute("""
CREATE TABLE IF NOT EXISTS bands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    genre TEXT,
    postcode TEXT,
    lat REAL,
    lon REAL,
    funding_goal INTEGER,
    current_amount INTEGER
)
""")

# Donations table
cursor.execute("""
CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    band_id INTEGER,
    amount INTEGER,
    date TEXT
)
""")

# Events table
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    band_id INTEGER,
    event_name TEXT,
    location TEXT,
    date TEXT
)
""")

# Insert sample data if empty
cursor.execute("SELECT COUNT(*) FROM bands")
if cursor.fetchone()[0] == 0:
    bands_data = [
        ("Echo Sound", "Rock", "BS16", 51.50, -2.54, 500, 120),
        ("Neon Lights", "Pop", "BS1", 51.45, -2.58, 300, 200),
        ("Street Vibes", "Hip-Hop", "BS16", 51.52, -2.55, 400, 150),
        ("Indie Pulse", "Indie", "BS8", 51.46, -2.62, 350, 80),
    ]

    cursor.executemany("""
    INSERT INTO bands (name, genre, postcode, lat, lon, funding_goal, current_amount)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, bands_data)

    events_data = [
        (1, "Live at Bristol Stage", "Bristol", "2026-05-01"),
        (2, "Pop Night", "City Centre", "2026-05-10"),
        (3, "Street Fest", "Outdoor Arena", "2026-06-01"),
    ]

    cursor.executemany("""
    INSERT INTO events (band_id, event_name, location, date)
    VALUES (?, ?, ?, ?)
    """, events_data)

    conn.commit()

# ---------------- FUNCTIONS ----------------

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate approximate distance using Euclidean formula (simplified)"""
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def get_all_genres():
    """Get list of all available genres"""
    cursor.execute("SELECT DISTINCT genre FROM bands ORDER BY genre")
    return [row[0] for row in cursor.fetchall()]

def get_all_postcodes():
    """Get list of all available postcodes"""
    cursor.execute("SELECT DISTINCT postcode FROM bands ORDER BY postcode")
    return [row[0] for row in cursor.fetchall()]

def search_bands(postcode, genre_filter=None):
    """Search bands by postcode and optional genre filter"""
    cursor.execute("SELECT * FROM bands")
    bands = cursor.fetchall()

    user_lat, user_lon = 51.50, -2.55  # mock user location

    results = []
    for band in bands:
        # Check if postcode matches (partial match)
        if postcode.upper() in band[3].upper():
            # Apply genre filter if provided
            if genre_filter and genre_filter.lower() not in band[2].lower():
                continue

            distance = calculate_distance(user_lat, user_lon, band[4], band[5])
            results.append((band, distance))

    # Sort by distance (closest first)
    results.sort(key=lambda x: x[1])
    return results

def show_events(band_id):
    """Display upcoming events for a specific band"""
    cursor.execute("SELECT event_name, location, date FROM events WHERE band_id=?", (band_id,))
    events = cursor.fetchall()

    if events:
        print("\n📅 Upcoming Events:")
        for e in events:
            print(f"   - {e[0]} at {e[1]} on {e[2]}")
    else:
        print("\n   No upcoming events found.")

def donate(band_id, amount):
    """Process a donation to a band"""
    cursor.execute("SELECT current_amount, funding_goal, name FROM bands WHERE id=?", (band_id,))
    result = cursor.fetchone()

    if result:
        current, goal, band_name = result
        new_total = current + amount

        # Update band's current amount
        cursor.execute("UPDATE bands SET current_amount=? WHERE id=?", (new_total, band_id))

        # Record donation in history
        cursor.execute("""
        INSERT INTO donations (band_id, amount, date)
        VALUES (?, ?, ?)
        """, (band_id, amount, datetime.now().strftime("%Y-%m-%d %H:%M")))

        conn.commit()

        percentage = (new_total / goal) * 100

        print("\n✅ Donation successful!")
        print(f"   Band: {band_name}")
        print(f"   💰 £{new_total} / £{goal}")
        print(f"   📊 Progress: {percentage:.2f}%")

        # Provide encouraging feedback based on progress
        if percentage >= 100:
            print("   🎉 Goal reached! You fully supported this band!")
        elif percentage >= 70:
            print("   🔥 Almost there! You made a big impact!")
        elif percentage >= 50:
            print("   💪 Halfway there! Keep supporting!")
        else:
            print("   👏 Every contribution helps!")
    else:
        print("\n❌ Band not found.")

def show_donation_history():
    """Display all donation history"""
    cursor.execute("""
    SELECT bands.name, donations.amount, donations.date
    FROM donations
    JOIN bands ON donations.band_id = bands.id
    ORDER BY donations.date DESC
    """)
    history = cursor.fetchall()

    if history:
        print("\n📜 Donation History:")
        total_donated = 0
        for h in history:
            print(f"   {h[0]} - £{h[1]} on {h[2]}")
            total_donated += h[1]
        print(f"\n   💵 Total Donated: £{total_donated}")
    else:
        print("\n📜 No donation history yet.")

def get_valid_menu_choice():
    """Keep asking until valid menu choice (1/2/3)"""
    while True:
        choice = input("Select option (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            return choice
        else:
            print("   ❌ Invalid option. Please enter 1, 2, or 3.")

def get_valid_postcode():
    """Keep asking until valid postcode is entered"""
    available_postcodes = get_all_postcodes()
    
    while True:
        postcode = input(f"Enter postcode (Available: {', '.join(available_postcodes)}): ").strip().upper()
        
        if not postcode:
            print("   ❌ Postcode cannot be empty.")
            continue
        
        # Check if postcode exists in database
        cursor.execute("SELECT COUNT(*) FROM bands WHERE postcode LIKE ?", (f"%{postcode}%",))
        if cursor.fetchone()[0] > 0:
            return postcode
        else:
            print(f"   ❌ No bands found in '{postcode}'.")
            print(f"   💡 Available postcodes: {', '.join(available_postcodes)}")

def get_valid_genre():
    """Get optional genre filter"""
    available_genres = get_all_genres()
    genre = input(f"Filter by genre (Available: {', '.join(available_genres)}) or press Enter to skip: ").strip()
    
    if not genre:
        return None
    
    # Check if genre exists
    if any(genre.lower() in g.lower() for g in available_genres):
        return genre
    else:
        print(f"   ⚠️ Genre '{genre}' not found, showing all genres.")
        return None

def get_valid_band_id(valid_ids):
    """Keep asking until valid band ID is entered"""
    while True:
        band_id_input = input(f"\nSelect band ID ({'/'.join(map(str, valid_ids))}): ").strip()
        
        try:
            band_id = int(band_id_input)
            if band_id in valid_ids:
                return band_id
            else:
                print(f"   ❌ Invalid band ID. Please choose from: {', '.join(map(str, valid_ids))}")
        except ValueError:
            print("   ❌ Invalid input. Please enter a number.")

def get_yes_no_input(prompt):
    """Get yes/no input from user"""
    while True:
        response = input(prompt).strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
            return False
        else:
            print("   ❌ Invalid input. Please enter 'yes' or 'no'.")

def get_valid_donation_amount():
    """Keep asking until valid donation amount (5-25) is entered"""
    while True:
        amount_input = input("Enter amount (£5-£25): £").strip()
        
        try:
            amount = int(amount_input)
            if 5 <= amount <= 25:
                return amount
            else:
                print(f"   ❌ Amount must be between £5 and £25. You entered: £{amount}")
        except ValueError:
            print("   ❌ Invalid input. Please enter a whole number (e.g., 10).")

# ---------------- MAIN APP ----------------

print("=" * 40)
print("🎵 Welcome to LocalWave 🎵")
print("Support Local Bands in Your Community!")
print("=" * 40)

try:
    while True:
        print("\n" + "─" * 40)
        print("--- MAIN MENU ---")
        print("1. Search Bands")
        print("2. View Donation History")
        print("3. Exit")
        print("─" * 40)

        choice = get_valid_menu_choice()

        if choice == "1":
            # --- SEARCH BANDS ---
            print("\n🔍 Band Search")
            
            # Get valid postcode
            postcode = get_valid_postcode()
            
            # Get optional genre filter
            genre = get_valid_genre()

            # Search for bands
            results = search_bands(postcode, genre)

            if not results:
                print("\n   ❌ No bands found matching your criteria.")
                print("   💡 Try a different postcode or skip the genre filter.")
                continue

            print("\n🎤 Bands Near You:")
            print("─" * 60)
            valid_ids = []
            for band, dist in results:
                band_id, name, genre, pc, lat, lon, goal, current = band
                percentage = (current / goal) * 100
                valid_ids.append(band_id)
                print(f"ID: {band_id} | {name} ({genre})")
                print(f"   📍 {pc} - {dist:.2f} km away")
                print(f"   💰 £{current}/{goal} ({percentage:.1f}% funded)")
                print("─" * 60)

            # Select band
            band_id = get_valid_band_id(valid_ids)

            # Show events for selected band
            show_events(band_id)

            # Ask if user wants to donate
            if get_yes_no_input("\nDo you want to donate? (yes/no): "):
                amount = get_valid_donation_amount()
                donate(band_id, amount)
            else:
                print("   👍 No problem! You can donate anytime.")

        elif choice == "2":
            # --- VIEW DONATION HISTORY ---
            show_donation_history()

        elif choice == "3":
            # --- EXIT ---
            print("\n" + "=" * 40)
            print("👋 Thank you for supporting local music!")
            print("Goodbye!")
            print("=" * 40)
            break

except KeyboardInterrupt:
    print("\n\n⚠️ Program interrupted by user.")
    print("Goodbye!")

finally:
    # Ensure database connection is closed
    conn.close()
    print("🔒 Database connection closed.")