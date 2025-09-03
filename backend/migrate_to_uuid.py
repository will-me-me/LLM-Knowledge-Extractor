"""
Migration script to convert integer ID to UUID
Run this script to migrate your existing database
"""

from sqlalchemy import create_engine, text
import os

# Database connection
SQLALCHEMY_DATABASE_URL = "postgresql://myroot:root@localhost/mydatabase"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def migrate_to_uuid():
    """Migrate existing integer IDs to UUIDs"""
    
    with engine.connect() as connection:
        # Start a transaction
        trans = connection.begin()
        
        try:
            print("Starting migration from integer ID to UUID...")
            
            # Step 1: Enable uuid-ossp extension (if not already enabled)
            print("Enabling uuid-ossp extension...")
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
            
            # Step 2: Add a new UUID column
            print("Adding new UUID column...")
            connection.execute(text("""
                ALTER TABLE extractions 
                ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
            """))
            
            # Step 3: Update all existing rows to have UUIDs
            print("Generating UUIDs for existing records...")
            connection.execute(text("""
                UPDATE extractions 
                SET new_id = uuid_generate_v4() 
                WHERE new_id IS NULL;
            """))
            
            # Step 4: Drop the old primary key constraint
            print("Dropping old primary key constraint...")
            connection.execute(text("""
                ALTER TABLE extractions 
                DROP CONSTRAINT extractions_pkey;
            """))
            
            # Step 5: Drop the old id column
            print("Dropping old integer id column...")
            connection.execute(text("""
                ALTER TABLE extractions 
                DROP COLUMN id;
            """))
            
            # Step 6: Rename new_id to id
            print("Renaming new_id column to id...")
            connection.execute(text("""
                ALTER TABLE extractions 
                RENAME COLUMN new_id TO id;
            """))
            
            # Step 7: Add primary key constraint to new UUID column
            print("Adding primary key constraint to UUID column...")
            connection.execute(text("""
                ALTER TABLE extractions 
                ADD CONSTRAINT extractions_pkey PRIMARY KEY (id);
            """))
            
            # Step 8: Create index on the new UUID column
            print("Creating index on UUID column...")
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_extractions_id 
                ON extractions (id);
            """))
            
            # Commit the transaction
            trans.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"Migration failed: {str(e)}")
            raise e

def verify_migration():
    """Verify the migration was successful"""
    
    with engine.connect() as connection:
        # Check the column type
        result = connection.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'extractions' AND column_name = 'id';
        """))
        
        row = result.fetchone()
        if row:
            print(f"Column 'id' type: {row[1]}")
            if row[1] == 'uuid':
                print("✅ Migration successful - ID column is now UUID type")
            else:
                print("❌ Migration may have failed - ID column is not UUID type")
        else:
            print("❌ Could not find ID column")
        
        # Check if we have any data
        result = connection.execute(text("SELECT COUNT(*) FROM extractions;"))
        count = result.fetchone()[0]
        print(f"Total records in table: {count}")

if __name__ == "__main__":
    # Run migration
    migrate_to_uuid()
    
    # Verify migration
    verify_migration()
    
    print("\nMigration complete! You can now use your FastAPI application with UUID IDs.")