from flask import Flask, request, jsonify, render_template, redirect, url_for
from rdflib import Graph
import spacy
import sys
import os
from helpers.question_answer import process_query
import time
import pickle
from pathlib import Path

# adding Folder_2 to the system path
#sys.path.insert(0, 'C:\Users\shiva\Music\Resume\Projects\Geological-Ontology\Flask_project\helpers')
#sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

app = Flask(__name__)
app.config['setup_complete'] = False  # Track setup state

# Load pre-warmed setup data at startup
path = Path("setup_data.pkl")
with open(path, "rb") as f:
    g, nlp, ontology_terms, matcher, classes, relations, descriptions, ontology_terms_mapping = pickle.load(f)



@app.route("/")
def home():
    #return "Welcome to the Geological Q&A System!"
    return render_template("index.html")

# Setup route
@app.route('/setup', methods=['POST'])
def setup():
    # Your setup logic here

    if not app.config['setup_complete']:
        start_time = time.time()
        # Initialize reusable resources and store them in app config
        #g, nlp, ontology_terms, matcher, classes, relations, description, ontology_terms_mapping = initialize_resources()
        app.config["G"] = g
        app.config["NLP"] = nlp
        app.config["ONTOLOGY_TERMS"] = ontology_terms
        app.config["MATCHER"] = matcher
        app.config["CLASSES"] = classes
        app.config["RELATIONS"] = relations
        app.config["DESCRIPTION"] = descriptions
        app.config["ONTOLOGY_MAPPING"] = ontology_terms_mapping
        app.config['setup_complete'] = True

    # Initialize resources when the app starts
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Query execution time: {execution_time:.4f} seconds")

    print("Setup function called!")
    return redirect(url_for('question_page'))

@app.route("/question")
def question_page():
    return render_template("question-answer.html")

@app.route("/query", methods=["POST"])
def query():
    data = request.json # Expect JSON input
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question provided"}), 400
    else:
        # Retrieve initialized resources from app config
        g = app.config["G"]
        nlp = app.config["NLP"]
        ontology_terms = app.config["ONTOLOGY_TERMS"]
        matcher = app.config["MATCHER"]
        classes = app.config["CLASSES"]
        relations = app.config["RELATIONS"]
        description = app.config["DESCRIPTION"]
        ontology_terms_mapping = app.config["ONTOLOGY_MAPPING"]
        results = process_query(g, question, nlp, ontology_terms, matcher, classes, relations, description, ontology_terms_mapping)
        return jsonify({
            "question": question,
            "results": results
        }), 200

if __name__ == "__main__":
    app.run()

