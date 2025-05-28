import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UnlimitedDocWorks.main_pipe import RAGCSVSystemClaude  # now this works


pdf_dir = "../UnlimitedDocWorks/archive"  # folder containing PDF files
db_file = "../UnlimitedDocWorks/sqlite_store/supplychain.sqlite"
system = RAGCSVSystemClaude(pdf_dir=pdf_dir, db_file=db_file)
system.load_data()

from flask import Flask, request, jsonify  # make sure this has your `.run()` method
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/run", methods=["POST"])
def run():
    data = request.get_json()
    user_text = data.get("text", "")
    mode = data.get("mode", "document") 
    print(mode)
    result = system.run(user_text,source = mode)
    #print(result)
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(debug=True)
