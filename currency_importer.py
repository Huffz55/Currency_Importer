import requests
import xml.etree.ElementTree as ET
import psycopg2
from datetime import datetime
import sys
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"ERROR: Could not connect to database: {e}", file=sys.stderr)
        return None

def fetch_tcmb_data():
    """Fetches daily currency XML data from TCMB and returns the XML root."""
    try:
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        
        xml_content = response.content.decode('utf-8')
        root = ET.fromstring(xml_content)
        return root
        
    except requests.exceptions.Timeout:
        print("ERROR: Request to TCMB API timed out.", file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
    except ET.ParseError as e:
        print(f"ERROR: Failed to parse XML (data might be corrupt): {e}", file=sys.stderr)
    return None

def process_and_insert_data(conn, xml_root):
    """Parses XML data and inserts it into the database."""
    try:
        bulletin_date_str = xml_root.get('Tarih')
        date_iso = datetime.strptime(bulletin_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        try:
            date_iso = datetime.strptime(bulletin_date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
        except Exception as e:
            print(f"ERROR: Could not parse date from XML: {bulletin_date_str}. Error: {e}", file=sys.stderr)
            return
            
    print(f"Processing data for date: {date_iso}")
    
    currencies_to_insert = []
    
    for currency in xml_root.findall('Currency'):
        code = currency.get('CurrencyCode')
        buy_rate = currency.find('ForexBuying').text
        sell_rate = currency.find('ForexSelling').text

        if code and buy_rate and sell_rate and buy_rate.strip() and sell_rate.strip():
            currencies_to_insert.append((date_iso, code, buy_rate, sell_rate))

    if not currencies_to_insert:
        print("No valid currency data found to process.")
        return

    insert_query = """
    INSERT INTO kurlar (tarih, kur_kodu, alis_fiyati, satis_fiyati)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (tarih, kur_kodu) 
    DO UPDATE SET 
        alis_fiyati = EXCLUDED.alis_fiyati,
        satis_fiyati = EXCLUDED.satis_fiyati;
    """

    
    processed_count = 0
    try:
        with conn.cursor() as cursor:
            for rate in currencies_to_insert:
                cursor.execute(insert_query, rate)

                if cursor.rowcount > 0:
                    processed_count += 1
                    print(f"   -> PROCESSED: {rate[1]} (Inserted or Updated)")

        conn.commit() 
        print(f"\nOperation complete. {processed_count} currency rates processed (inserted/updated).")
        
    except psycopg2.Error as e:
        print(f"ERROR: Database insert failed: {e}", file=sys.stderr)
        conn.rollback() 

def main():
    """Main function to run the importer."""
    print("Currency Importer started...")
    conn = get_db_connection()
    if conn is None:
        sys.exit(1) 
        
    try:
        xml_root = fetch_tcmb_data()
        if xml_root is not None:
            process_and_insert_data(conn, xml_root)
    finally:
        if conn:
            conn.close() 
            print("Database connection closed.")

if __name__ == "__main__":
    main()