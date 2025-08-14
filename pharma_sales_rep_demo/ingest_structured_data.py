import os
import json
import pandas as pd
import argparse
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
from pymongo.errors import PyMongoError
from dotenv import load_dotenv


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Ingest product data into MongoDB.')
    parser.add_argument('--data-file', type=str, default='./data/dr_reddys_products.json',
                        help='Path to the product data JSON file')
    parser.add_argument('--env-file', type=str, default='./.env',
                        help='Path to the environment file')
    parser.add_argument('--db-name', type=str, default='dr_reddys',
                        help='MongoDB database name')
    parser.add_argument('--collection-name', type=str, default='product_inventory',
                        help='MongoDB collection name')
    parser.add_argument('--clear-existing', action='store_true',
                        help='Clear existing documents in the collection')
    return parser.parse_args()


def load_product_data(file_path):
    """Load product data from JSON file into a pandas DataFrame."""
    try:
        with open(file_path, 'r') as fread:
            data = [json.loads(line) for line in fread.readlines()]
        df = pd.DataFrame.from_records(data)
        print(f"Successfully loaded {len(df)} products from {file_path}")
        return df
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading data: {e}")
        return None


def connect_to_mongodb(env_file, db_name, collection_name):
    """Establish connection to MongoDB using environment variables."""
    try:
        load_dotenv(dotenv_path=env_file) # replace with .env file path if needed
        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client[db_name]
        collection = db[collection_name]
        print(f"Successfully connected to MongoDB database '{db_name}', collection '{collection_name}'")
        return collection
    except PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}")
        return None


def insert_data_to_mongodb(collection, df, clear_existing=True):
    """Insert data into MongoDB collection."""
    try:
        # Check if collection has documents
        if clear_existing and collection.count_documents({}) > 0:
            print("Collection already has documents. Clearing existing data...")
            collection.delete_many({})  # Clear existing documents
        elif collection.count_documents({}) > 0:
            print(f"Collection already has {collection.count_documents({})} documents. Adding new data...")
        
        # Convert DataFrame to list of dictionaries and insert
        records = json.loads(df.to_json(orient="records"))
        collection.insert_many(records)
        print(f"Successfully inserted {len(records)} documents into MongoDB")
    except PyMongoError as e:
        print(f"Error inserting data: {e}")


def create_search_index(collection):
    """Create full-text search index on the collection."""
    try:
        collection.create_search_index(
            model=SearchIndexModel(
                name="full_text_search_index",
                definition={
                    "dynamic": True,
                    "fields": {
                        "search_text": {
                            "type": "string",
                            "analyzer": "lucene.standard"
                        }
                    }
                }
            )
        )
        print("Successfully created full-text search index")
    except PyMongoError as e:
        print(f"Error creating search index: {e}")


def main():
    """Main function to orchestrate the data ingestion process."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Load data
    df = load_product_data(args.data_file)
    if df is None:
        return
    
    # Display sample data
    print("\nSample data:")
    print(df.head())
    
    # Connect to MongoDB
    collection = connect_to_mongodb(args.env_file, args.db_name, args.collection_name)
    if collection is None:
        return
    
    # Insert data into MongoDB
    insert_data_to_mongodb(collection, df, args.clear_existing)
    
    # Create search index
    create_search_index(collection)
    
    print("Data ingestion process completed successfully")


if __name__ == "__main__":
    main()
