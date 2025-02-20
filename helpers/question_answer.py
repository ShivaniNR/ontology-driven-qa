import re
from rdflib import Graph, Namespace, RDF, RDFS
import spacy
from spacy.matcher import PhraseMatcher
from socket_manager import socketio
import time

#helper
def format_term(term, ontology_terms_mapping):
    if term in ontology_terms_mapping:
        return ontology_terms_mapping[term]

#preprocessing of question
def preprocess_question(question, nlp):
    question = question.lower()
    question = re.sub(r'[^\w\s]', '', question)  # Remove special characters
    doc = nlp(question)
    lemmatized = " ".join([token.lemma_ for token in doc])  # Lemmatize the question
    return lemmatized

# Identify question intent
def identify_intent_and_focus(question, nlp, matcher):
    doc = nlp(question)
    matches = matcher(doc)
    extracted_terms = [doc[start:end].text for match_id, start, end in matches]
    #print('extracted_terms', extracted_terms)
    #print(doc)
    
    
    # Default intent and focus terms
    intent = "unknown"
    focus_terms = []
    
    # for token in doc:
    #     print(token, token.head, token.pos_, token.tag_, token.dep_)
    
    # Find root verb and its dependencies
    root = [token for token in doc if token.head == token][0]
    
    # for child in root.children:
    #     print(child, child.dep_)
    
    # Classification intent (e.g., "Types of X?", "What are Y?")
    if any(token.lemma_ in ["type", "unit", "kind", "different", "subclass", "category", "group", "form", "classification"] for token in doc):
        intent = "classification"
        
    # Definition intent (e.g., "What is X?")
    elif root.lemma_ in ["be", "define", "explain"]:  # Check for linking or defining verbs dynamically
        #print('inside definition')
        intent = 'definition'
        
    focus_terms = extracted_terms

    
    # Remove stopwords and irrelevant terms from focus_terms
    focus_terms = [term for term in focus_terms if term not in nlp.Defaults.stop_words]
    #print('final intent', intent, ' and final terms ', focus_terms)

    return intent, focus_terms

#Generate SPARQL query
def generate_dynamic_sparql_query(intent, focus_terms, relations, ontology_terms_mapping):
    if not focus_terms:
        return None
    
    #print('focus ',focus_terms)
    #print('intent ',intent)
    
    focus_term = focus_terms[0]
    
    transformed_term = format_term(focus_term, ontology_terms_mapping)
    
    if intent == "definition" and transformed_term:
        # return f"""
        # SELECT DISTINCT ?comment
        # WHERE {{
        #     :{transformed_term} rdfs:comment ?comment .
        # }}
        # """
        return f"""
            SELECT DISTINCT ?comment 
                   (GROUP_CONCAT(DISTINCT COALESCE(?subClassEntity, "None"); separator=", ") AS ?subClassList)
                   (GROUP_CONCAT(DISTINCT COALESCE(?typeEntity, "None"); separator=", ") AS ?typeList)
            WHERE {{
                OPTIONAL {{ :{transformed_term} rdfs:comment ?comment . }}
                OPTIONAL {{ ?subClassEntity rdfs:subClassOf :{transformed_term} . FILTER(BOUND(?subClassEntity)) }}
                OPTIONAL {{ :{transformed_term} rdf:type ?typeEntity . FILTER(BOUND(?typeEntity)) }}
            }}
            GROUP BY ?comment
        """
            # return f"""
            # SELECT DISTINCT ?comment (GROUP_CONCAT(DISTINCT ?related; separator=", ") AS ?relatedList)
            # WHERE {{
            #     OPTIONAL {{ :{transformed_term} rdfs:comment ?comment . }}
            #     OPTIONAL {{ ?related rdfs:subClassOf :{transformed_term} . }}
            #     OPTIONAL {{ :{transformed_term} rdf:type ?related . }}
            # }}
            # GROUP BY ?comment
            # """
    elif intent == "classification" and transformed_term:
        if focus_term in relations:
            return f"""
            SELECT DISTINCT ?child
            WHERE {{
                ?child rdfs:subClassOf :{transformed_term} .
            }}
            """
         # Check if the focus term is a child class
        for parent, children in relations.items():
            if focus_term in children:
                return f"""
                SELECT DISTINCT ?subclass
                WHERE {{
                    ?subclass rdfs:subClassOf :{transformed_term} .
                }}
                """
    
    return None

#Questions:
def process_question_dynamic(g, question, nlp, ontology_terms, matcher, classes, relations, description, ontology_terms_mapping):
    processed_question = preprocess_question(question, nlp)
    socketio.emit('execution_step', {"step": "Query preprocessed", "status": "success"})
    #print('processed_question ', processed_question)
    #to handle description queries
    intent, focus_terms = identify_intent_and_focus(processed_question, nlp, matcher)
    if not intent or not focus_terms:
        socketio.emit('execution_step', {"step": "Could not identitfy the query", "status": "error"})
        return None
    else:
        socketio.emit('execution_step', {"step": "Identified the query", "status": "success"})

    sparql_query = generate_dynamic_sparql_query(intent, focus_terms, relations, ontology_terms_mapping)

    #print(sparql_query)
    if sparql_query:
        socketio.emit('execution_step', {"step": "Searching in the Graph", "status": "success"})
        time.sleep(3)
        results = g.query(sparql_query)
        if results:
            socketio.emit('execution_step', {"step": "Found results!", "status": "success"})
            time.sleep(1)
            if intent == 'definition':
                comment = []
                related_terms = {
                    'subClasses': [], 
                    'instanceOf': []
                }
                for row in results:
                    comment = str(row[0])

                    entity_types = row['typeList'].split(',')
                    if any(obj.split('#')[-1] == 'NamedIndividual' for obj in entity_types):
                        for obj in entity_types:
                            if obj.split('#')[-1] != 'NamedIndividual':
                                related_terms['instanceOf'].append(obj)
                    elif any(obj.split('#')[-1] == 'Class' for obj in entity_types):
                        if str(row['subClassList']) != 'None':
                            for entity in row['subClassList'].split(','):
                                related_terms['subClasses'].append(str(entity))
                return [comment, related_terms], intent
            
            elif intent == 'classification':
                return [str(row[0]) for row in results], intent
        else:
            socketio.emit('execution_step', {"step": "Search Failed!", "status": "error"})
            return []
    socketio.emit('execution_step', {"step": "Search Failed!", "status": "error"})
    return []

#Answers:
# Process answers to extract readable terms
def process_answer_term(term):
    term = term.replace("_", " ")
    return term

def process_answers(answers, intent):
    if intent == 'definition':
        processed_answer = {}
        processed_answer['comment'] = str(answers[0])
        
        related_terms = answers[1]
        if len(related_terms['subClasses']) != 0:
            processed_answer['subClasses'] = []
            for subClass in related_terms['subClasses']:
                split_answer = subClass.split('#')
                processed_answer['subClasses'].append(process_answer_term(split_answer[-1]))
        if len(related_terms['instanceOf']) != 0:
            processed_answer['instanceOf'] = []
            for subClass in related_terms['instanceOf']:
                split_answer = subClass.split('#')
                processed_answer['instanceOf'].append(process_answer_term(split_answer[-1]))
        return processed_answer
    
    processed_answer = []
    for answer in answers:
        split_answer = answer.split('#')
        processed_answer.append(process_answer_term(split_answer[-1]))
    return processed_answer

#Query:
def process_query(g, question, nlp, ontology_terms, matcher, classes, relations, description, ontology_terms_mapping):
    socketio.emit('execution_step', {"step": "Query received", "status": "success"})
    answers = process_question_dynamic(g, question, nlp, ontology_terms, matcher, classes, relations, description, ontology_terms_mapping)
    if answers:
        modified_answer = process_answers(answers[0], answers[1])
        socketio.emit('execution_step', {"step": "Formatting answer", "status": "success"})
        socketio.emit('execution_step', {"step": "Process complete", "status": "success"})
        return modified_answer
    else:
        return 'No Data Found. Check the entities or reformate the question.'
    


    

"""
Tasks remaining:
1. check process_answer_term, why during the definition query, the first letter is small case?
2. modularize the file
"""