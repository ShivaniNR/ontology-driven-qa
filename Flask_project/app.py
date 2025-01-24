from flask import Flask, request, jsonify
from rdflib import Graph
import spacy
import sys
import os
from helpers.setup import initialize_resources
from helpers.question_answer import process_query

# adding Folder_2 to the system path
#sys.path.insert(0, 'C:\Users\shiva\Music\Resume\Projects\Geological-Ontology\Flask_project\helpers')
#sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

app = Flask(__name__)


# Initialize reusable resources and store them in app config
def initialize_app_resources():
    g, nlp, ontology_terms, matcher, classes, relations, description, ontology_terms_mapping = initialize_resources()
    app.config["G"] = g
    app.config["NLP"] = nlp
    app.config["ONTOLOGY_TERMS"] = ontology_terms
    app.config["MATCHER"] = matcher
    app.config["CLASSES"] = classes
    app.config["RELATIONS"] = relations
    app.config["DESCRIPTION"] = description
    app.config["ONTOLOGY_MAPPING"] = ontology_terms_mapping

# Initialize resources when the app starts
initialize_app_resources()

@app.route("/")
def home():
    return "Welcome to the Geological Q&A System!"

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
    app.run(debug=True)

