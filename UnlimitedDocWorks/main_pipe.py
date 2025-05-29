import os
import re
import json
import sqlite3
import requests
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


import requests

CLAUDE_API_URL = "https://quchnti6xu7yzw7hfzt5yjqtvi0kafsq.lambda-url.eu-central-1.on.aws/"
CLAUDE_API_KEY = ""

def query_claude(prompt: str) -> dict:
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": CLAUDE_API_KEY,
        "prompt": prompt,
        "model_id": "claude-3.5-sonnet",
        "model_params": {
            "max_tokens": 512,
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(CLAUDE_API_URL, json=payload, headers=headers)
        print(response)
        response.raise_for_status()
        response_data = response.json()


        content = response_data.get("response", {}).get("content", [{}])[0].get("text", "").strip()

        message = response_data.get("response", {})
        content1 = message.get("content", [])
        output_text = content1[0].get("text", "").strip() if content1 else ""

        # Extract usage info
        usage = message.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        
        return {
            "text": content,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Error querying Claude: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


class RAGCSVSystemClaude:
    def __init__(self, pdf_dir: str, db_file: str):
        self.pdf_dir = pdf_dir
        self.db_file = db_file
        self.conn = None
        self.retriever = None

    def load_data(self):
        # Connect to the SQLite database
        self.conn = sqlite3.connect(self.db_file)
        self.load_embeddings()

    def load_embeddings(self):
        faiss_folder = "../UnlimitedDocWorks/vector_store"
        loaded_vector_store = FAISS.load_local(
            faiss_folder,
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-MpNet-base-v2"),
            allow_dangerous_deserialization=True
        )
        self.retriever = loaded_vector_store.as_retriever(search_type="similarity", k=4)

    def get_rag_answer(self, query: str) -> str:
        print("starting rag answer")

        docs = self.retriever.get_relevant_documents(query)
        context = "\n\n".join([doc.page_content for doc in docs[:4]])

        prompt = f"""
        You are a highly analytical assistant with deep understanding of logistics, supply chain, and policy interpretation. 
        Your task is to precisely answer the question below using the provided company documentation. Keep it concise.
        If the answer is not explicitly stated, you must provide a reasoned inference based on the available information.

        Context:
        {context}

        Question: {query}

        Answer (with reasoning if needed):
        """
        result = query_claude(prompt)
        print(result)
        print(f"Input Tokens: {result['input_tokens']}")
        print(f"Output Tokens: {result['output_tokens']}")
        print(f"Total Tokens: {result['total_tokens']}")
        return result["text"]

    def lookup_order_stats(self, query: str):
        if self.conn is None:
            self.load_data()
        db_file = "../UnlimitedDocWorks/sqlite_store/supplychain.sqlite"
        self.conn = sqlite3.connect(db_file)

        # Fetch column names from SQLite
        column_query = "PRAGMA table_info(shipping_data);"
        #print(column_query)
        columns_info = self.conn.execute(column_query).fetchall()
        columns = [col[1] for col in columns_info]

        prompt = f"""
        You are an advanced data analyst assistant. 
        Given a user's question and the dataset's column names, generate a valid **SQL query** that answers the question 
        using a SQLite database table called `shipping_data`.

        Only return the SQL query — no explanations, no text, no comments.
        Do not invent functions or column names.
        Columns available in the dataset:
        {', '.join(columns)}

        Question: {query}

        SQL query:
        """

        result = query_claude(prompt)
        print(f"Input Tokens: {result['input_tokens']}")
        print(f"Output Tokens: {result['output_tokens']}")
        print(f"Total Tokens: {result['total_tokens']}")

        try:
            result = self.conn.execute(sql_query)
            return result.fetchall()
        except Exception as e:
            return f"Error processing the query: {str(e)}"

    def get_column_samples(self, table_name="shipping_data", sample_count=5):
        sample_data = {}
        columns_info = self.conn.execute(f"PRAGMA table_info({table_name});").fetchall()
        columns = [col[1] for col in columns_info]

        for col in columns:
            # Try to check if the column is categorical (non-numeric)
            try:
                # Check if there are mostly text or categorical data
                result = self.conn.execute(f"""
                    SELECT DISTINCT "{col}"
                    FROM {table_name}
                    WHERE "{col}" IS NOT NULL
                    LIMIT {sample_count};
                """).fetchall()
                sample_values = [str(row[0]) for row in result]
                # If it looks like a categorical column (non-numeric), add it to the sample data
                if sample_values and not any(value.replace(".", "", 1).isdigit() for value in sample_values):
                    sample_data[col] = sample_values
            except Exception as e:
                sample_data[col] = ["<error>"]
        
        return sample_data


    def lookup_order_stats_with_context(self, query: str, document_context: str = ""):
        if self.conn is None:
            self.load_data()
        db_file = "../UnlimitedDocWorks/sqlite_store/supplychain.sqlite"
        self.conn = sqlite3.connect(db_file)

        print("reached context lookup")
        column_query = "PRAGMA table_info(shipping_data);"
        columns_info = self.conn.execute(column_query).fetchall()
        columns = [col[1] for col in columns_info]

        # Get column samples (categorical only)
        sample_values = self.get_column_samples()

        # Format column samples for the prompt
        sample_text = "\n".join([
            f"- {col}: {', '.join(vals)}" for col, vals in sample_values.items()
        ])

        final_prompt = f"""
        You are an expert SQL generator.

        🎯 Goal:
        Generate a valid SQLite SQL query using only the column names listed below, for a single table called shipping_data. Try to construct a query as simple as possible. Output only the query.

        🧾 Column Value Examples:
        {sample_text}    

        ⚠️ RULES:
        - Use only valid SQLite SQL functions.
        - Do NOT make up column names or wrap them in parentheses.
        - Output ONLY raw SQL — no commentary or markdown.
        - Check for precedence in logical operators in your query.



        📘 Business logic inferred from company documents:
        {document_context.strip()}

        🧑 User question:
        {query}

        SQL:
        """

        result = query_claude(final_prompt)
        print(f"Input Tokens: {result['input_tokens']}")
        print(f"Output Tokens: {result['output_tokens']}")
        print(f"Total Tokens: {result['total_tokens']}")
        sql_query = result["text"]        
        
        try:
            result = self.conn.execute(sql_query)
            return result.fetchall()
        except Exception as e:
            return f"Error processing the query: {str(e)}"

    def query(self, question: str, source: str):
        print("reached query function")

        if source == "csv":
            return self.lookup_order_stats(question)
        elif source == "document":
            return self.get_rag_answer(question)
        elif source == "document+csv":
            doc_answer = self.get_rag_answer(question)

            augmented_question = f"""
            The user question is: "{question}"

            Based on the following policy-related explanation, infer any definitions or assumptions needed:
            {doc_answer}

            Use the inferred definitions (if any) when generating the SQL query to answer the user question.
            """

            csv_answer = self.lookup_order_stats_with_context(augmented_question)

            return csv_answer
        

    def run(self, question: str, source: str = "documents"):
        return self.query(question, source)
