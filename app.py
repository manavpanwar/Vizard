from flask import Flask, render_template, request, jsonify
from langchain.llms import Ollama
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# MongoDB connection details
mongo_uri = "mongodb+srv://prince961:XRcDfeLA6foxoWtz@cluster0.ox5zuer.mongodb.net/CompanyDB?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client['CompanyDB']
collection = db['datasources']

# Create an instance of the Ollama model
ollama_instance = Ollama(base_url="http://122.176.146.28:11434", model="test20")

# Function to fetch column details from MongoDB
def fetch_column_details(document_id):
    document = collection.find_one({"_id": ObjectId(document_id)})
    if document and "ColumnDetails" in document:
        column_details = document["ColumnDetails"]
        columns_info = [
            {
                "Column Name": col["columnName"],
                "Data Type": col["dataType"],
                "UUID": col["uuid"]
            }
            for col in column_details
        ]
        return columns_info
    return None

# Function to prepare the initial query
def prepare_initial_query(columns_info):
    column_info_str = "\n".join(
        [f"Column Name: {col['Column Name']}, Data Type: {col['Data Type']}, UUID: {col['UUID']}" for col in columns_info]
    )
    return f"You are an expert in organizing pivot tables. Your task is to assist users in analyzing the following data:\n{column_info_str}\n.also always give uuid for every detail put in the table."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.form['query']
    document_id = "66f392a9a4a0c305c8c8f374"  # Replace with your actual document ID
    columns_info = fetch_column_details(document_id)
    
    if columns_info:
        initial_query = prepare_initial_query(columns_info)
        full_query = initial_query + f"Question: {user_query}\n.Please provide a detailed response.also always give uuid for every detail put in the table."
        
        # Get the response from the Ollama model
        response = ollama_instance(full_query)
        return jsonify({'response': response})
    return jsonify({'response': 'Error fetching column details.'})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)