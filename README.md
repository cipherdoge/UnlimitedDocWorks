![Do you have enough Docs in store?](public/ubw.jpg)

# UnlimitedDocWorks

**UnlimitedDocWorks** is a Retrieval-Augmented Generation (RAG) system designed to process both unstructured documents and structured CSV data. It enables intelligent querying across diverse data sources, using state-of-the-art language models and orchestration tools.

The system utilizes **Claude 3.5 Sonnet** for natural language understanding and **LangChain** for integrating data retrieval, parsing, and response generation workflows.

## Features

- Query over documents and CSVs with source-aware responses
- Support for both unstructured (e.g., PDFs, text files) and structured (e.g., tabular CSV) data
- Backed by Claude 3.5 Sonnet and LangChain for accurate, context-rich results
- Modular and extensible full-stack architecture

## Setup Instructions

Follow the steps below to set up the project locally.

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd UnlimitedDocWorks
```

### 2. Download Required Files

Access the required assets from the following Google Drive link and download both files:

[Google Drive – Project Files](https://drive.google.com/drive/folders/1-R7VIQaWKtpQAvBFB7_K44P5iaxx9i-j?usp=drive_link)

### 3. Place the SQLite File

Move the downloaded `.sqlite` file into the following directory:

```
UnlimitedDocWorks/sqlite_store/
```

### 4. Install Dependencies

Install the required Node.js and Python dependencies from the project root:

```bash
npm install
pip install -r requirements.txt
```

## Running the Application

The application requires both the backend and frontend services to be running in separate terminals.

### Terminal 1: Start the Backend

```bash
cd src
python backend.py
```

### Terminal 2: Start the Frontend

```bash
# From the project root
npm run dev
```

## License

This project is provided as-is under your chosen license. Ensure any third-party dependencies used comply with your intended usage and distribution.

