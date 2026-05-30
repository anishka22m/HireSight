from backend.db_connect import session
from backend.models import MarketTrend

def clear_old_trends():
    try:
        # Delete all records specifically from the MarketTrend table
        deleted_count = session.query(MarketTrend).delete()
        session.commit()
        print(f"✅ Successfully deleted {deleted_count} old duplicate records from the database!")
    except Exception as e:
        session.rollback()
        print(f"❌ Error clearing table: {e}")

if __name__ == "__main__":
    clear_old_trends()