from main_pipe import RAGCSVSystemClaude

# Define paths
pdf_dir = "archive"  # folder containing PDF files
db_file = "sqlite_store/supplychain.sqlite"

# Initialize the RAG system with the correct paths
system = RAGCSVSystemClaude(pdf_dir=pdf_dir, db_file=db_file)

# Load data (this is optional, you can call this when you need to load the database and PDFs)
system.load_data()  # this loads the FAISS vector store and the DuckDB connection

# Run queries
#print("=== CSV Query ===")
#csv_result = system.run("What is the total sales amount for all orders?", source="csv")
#print(csv_result)

#print("\n=== Document Query ===")
#document_result = system.run("What is our company's definition of no-movers?", source="document")
#print(document_result)

print("\n=== Combined Query ===")
combined_result = system.run("Which products that are classified as \"hazardous materials\" according to our HSE policy are currently being stored in facilities not certified for such materials?", source="document+csv")
print(combined_result)
