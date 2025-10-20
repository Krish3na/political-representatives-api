import os
import csv
import requests
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
    'postgresql://postgres:password@db:5432/legislators_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Legislator model
class Legislator(db.Model):
    __tablename__ = 'legislators'
    
    govtrack_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # sen/rep
    state = db.Column(db.String(2), nullable=False)
    district = db.Column(db.String(10))
    party = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(500))
    notes = db.Column(db.Text)

def download_legislators_data():
    url = "https://unitedstates.github.io/congress-legislators/legislators-current.csv"
    
    print("Downloading legislators data...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open('legislators-current.csv', 'w', newline='', encoding='utf-8') as f:
            f.write(response.text)
        
        print("Data downloaded successfully!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")
        return False

def create_tables():
    print("Creating database tables...")
    db.create_all()
    print("Tables created successfully!")

def parse_date(date_str):
    if not date_str:
        return None
    
    # Try different date formats
    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    print(f"Warning: Could not parse date: {date_str}")
    return None

def ingest_legislators():
    if not os.path.exists('legislators-current.csv'):
        print("CSV file not found. Downloading...")
        if not download_legislators_data():
            return False
    
    print("Starting data ingestion...")
    
    # Clear existing data
    Legislator.query.delete()
    db.session.commit()
    print("Cleared existing data")
    
    legislators_added = 0
    legislators_skipped = 0
    
    with open('legislators-current.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            try:
                # Extract required fields
                govtrack_id = int(row.get('govtrack_id', 0))
                if not govtrack_id:
                    legislators_skipped += 1
                    continue
                
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                birthday_str = row.get('birthday', '').strip()
                gender = row.get('gender', '').strip()
                type_val = row.get('type', '').strip()
                state = row.get('state', '').strip()
                district = row.get('district', '').strip()
                party = row.get('party', '').strip()
                url = row.get('url', '').strip()
                
                # Validate required fields
                if not all([first_name, last_name, gender, type_val, state, party]):
                    print(f"Skipping legislator {govtrack_id}: Missing required fields")
                    legislators_skipped += 1
                    continue
                
                # Parse birthday
                birthday = parse_date(birthday_str)
                if not birthday:
                    print(f"Skipping legislator {govtrack_id}: Invalid birthday")
                    legislators_skipped += 1
                    continue
                
                # Create legislator record
                legislator = Legislator(
                    govtrack_id=govtrack_id,
                    first_name=first_name,
                    last_name=last_name,
                    birthday=birthday,
                    gender=gender,
                    type=type_val,
                    state=state,
                    district=district if district else None,
                    party=party,
                    url=url if url else None,
                    notes=None  # Default to None
                )
                
                db.session.add(legislator)
                legislators_added += 1
                
                # Commit in batches for better performance
                if legislators_added % 100 == 0:
                    db.session.commit()
                    print(f"Processed {legislators_added} legislators...")
                
            except (ValueError, KeyError) as e:
                print(f"Error processing row: {e}")
                legislators_skipped += 1
                continue
    
    # Final commit
    db.session.commit()
    
    print(f"\nData ingestion completed!")
    print(f"Legislators added: {legislators_added}")
    print(f"Legislators skipped: {legislators_skipped}")
    
    return True

def main():
    print("Starting legislators data ingestion...")
    
    try:
        # Create Flask application context
        with app.app_context():
            # Create tables
            create_tables()
            
            # Ingest data
            if ingest_legislators():
                print("Data ingestion completed successfully!")
            else:
                print("Data ingestion failed!")
                return False
                
    except Exception as e:
        print(f"Error during data ingestion: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()
