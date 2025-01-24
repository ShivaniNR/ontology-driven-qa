import re
from rdflib import Graph, Namespace, RDF, RDFS
import spacy
from spacy.matcher import PhraseMatcher

#load the file
def load_ontology_file(file):
    ontology_file = file  # Path to your OWL file
    g = Graph()
    g.parse(ontology_file)
    return g

#helper function
# Preprocess terms (replace underscores, lowercase, lemmatize)
def preprocess_term(term, nlp):
    term = term.replace("_", " ").lower()
    doc = nlp(term)
    lemmatized = " ".join([token.lemma_ for token in doc])
    return lemmatized

def extract_terms_from_links(term, ontology_terms_mapping, nlp):
    extracted_term = term.split('#')[-1]
    processed_term = preprocess_term(extracted_term, nlp)
    if processed_term not in ontology_terms_mapping:
        ontology_terms_mapping[processed_term] = extracted_term
    return processed_term

# Extract ontology structure dynamically
def extract_ontology_structure(graph, ontology_terms_mapping, nlp):
    classes = set()
    relations = {}
    description = {}
    
    for s, p, o in graph:
        #print(s, p)
        if p == RDFS.subClassOf:
            parent = extract_terms_from_links(o, ontology_terms_mapping, nlp)   #need to change the name
            child = extract_terms_from_links(s, ontology_terms_mapping, nlp)
            classes.add(parent)
            classes.add(child)
            if parent not in relations:
                relations[parent] = []
            relations[parent].append(child)
        elif p == RDFS.comment:
            parent = extract_terms_from_links(s, ontology_terms_mapping, nlp)
            comment = str(o)
            description[parent] = comment 
    return list(classes), relations, description


# Initialize reusable resources #Reformate this function and create small functions 
def initialize_resources():
    #load the file
    ontology_file = "data/geological_ontology.rdf"  # Path to your OWL file
    g = Graph()
    g.parse(ontology_file)

    # Define namespaces (adjust based on your RDF file)
    GEO = Namespace("http://www.semanticweb.org/ontologies/2022/6/geological_taxonomy#")
    ontology_terms_mapping = dict()

    # Load the spaCy model
    nlp = spacy.load("en_core_web_sm")

    # Extract ontology structure dynamically
    classes, relations, description = extract_ontology_structure(g, ontology_terms_mapping, nlp)

    # Generate dynamic term list
    ontology_terms = {"parent": [], "children": [], 'instances': []}
    for parent, children in relations.items():
        ontology_terms["parent"].append(parent)
        ontology_terms["children"].extend(children)
    
    for instance, comment in description.items():
        ontology_terms["instances"].append(instance)

    # Use PhraseMatcher with dynamically generated terms
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp(term) for term in ontology_terms["parent"] + ontology_terms["children"] + ontology_terms['instances']]
    matcher.add("OntologyTerms", patterns)
    return g, nlp, ontology_terms, matcher, classes, relations, description, ontology_terms_mapping



'''
Tasks:
1. modularize the file
'''