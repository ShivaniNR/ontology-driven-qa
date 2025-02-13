import spacy
from rdflib import Graph, Namespace, RDFS
from spacy.matcher import PhraseMatcher
from concurrent.futures import ThreadPoolExecutor

# Constants
ONTOLOGY_FILE = "data/geological_ontology.rdf"
GEO = Namespace("http://www.semanticweb.org/ontologies/2022/6/geological_taxonomy#")

# Helper Functions
def preprocess_term(term, nlp):
    """Preprocess terms by replacing underscores, converting to lowercase, and lemmatizing."""
    term = term.replace("_", " ").lower()
    return " ".join([token.lemma_ for token in nlp(term)])

def extract_terms_from_links(term, ontology_terms_mapping, nlp):
    """Extract and preprocess terms from ontology links."""
    extracted_term = term.split('#')[-1]
    processed_term = preprocess_term(extracted_term, nlp)
    ontology_terms_mapping.setdefault(processed_term, extracted_term)
    return processed_term

def process_triple(triple, ontology_terms_mapping, nlp):
    """Process each ontology triple asynchronously."""
    s, p, o = triple
    if p == RDFS.subClassOf:
        parent = extract_terms_from_links(o, ontology_terms_mapping, nlp)
        child = extract_terms_from_links(s, ontology_terms_mapping, nlp)
        return ('relation', parent, child)
    elif p == RDFS.comment:
        parent = extract_terms_from_links(s, ontology_terms_mapping, nlp)
        return ('description', parent, str(o))
    return None

# def extract_ontology_structure(graph, ontology_terms_mapping, nlp):
#     """Efficiently extract ontology structure using parallel processing."""
#     classes, relations, descriptions = set(), {}, {}

#     with ThreadPoolExecutor() as executor:
#         results = executor.map(lambda triple: process_triple(triple, ontology_terms_mapping, nlp), graph)

#     for result in results:
#         if result:
#             if result[0] == 'relation':
#                 parent, child = result[1], result[2]
#                 classes.update([parent, child])
#                 relations.setdefault(parent, []).append(child)
#             elif result[0] == 'description':
#                 descriptions[result[1]] = result[2]

#     return list(classes), relations, descriptions
def extract_ontology_structure(graph, ontology_terms_mapping, nlp):
    """Efficiently extract ontology structure using batched processing."""
    classes, relations, descriptions = set(), {}, {}

    # Filter and iterate over relevant triples only
    subclass_triples = graph.query("""
        SELECT ?s ?o
        WHERE { ?s rdfs:subClassOf ?o . }
    """)
    comment_triples = graph.query("""
        SELECT ?s ?comment
        WHERE { ?s rdfs:comment ?comment . }
    """)

    # Process subClassOf relationships
    for s, o in subclass_triples:
        parent = extract_terms_from_links(o, ontology_terms_mapping, nlp)
        child = extract_terms_from_links(s, ontology_terms_mapping, nlp)
        classes.update([parent, child])
        relations.setdefault(parent, []).append(child)

    # Process comments
    for s, comment in comment_triples:
        parent = extract_terms_from_links(s, ontology_terms_mapping, nlp)
        descriptions[parent] = str(comment)

    return list(classes), relations, descriptions


def setup_spacy_matcher(nlp, ontology_terms):
    """Setup a PhraseMatcher for ontology terms."""
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp(term) for term in ontology_terms["parent"] + ontology_terms["children"] + ontology_terms['instances']]
    matcher.add("OntologyTerms", None, *patterns)
    return matcher

def initialize_resources():
    """Load and process the ontology efficiently."""
    g = Graph()
    g.parse(ONTOLOGY_FILE)

    #nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])  # Load only necessary components
    nlp = spacy.load("en_core_web_sm", disable=['ner'])
    ontology_terms_mapping = {}

    classes, relations, descriptions = extract_ontology_structure(g, ontology_terms_mapping, nlp)

    # Organize terms
    ontology_terms = {
        "parent": list(relations.keys()),
        "children": [child for children in relations.values() for child in children],
        "instances": list(descriptions.keys()),
    }

    matcher = setup_spacy_matcher(nlp, ontology_terms)

    return g, nlp, ontology_terms, matcher, classes, relations, descriptions, ontology_terms_mapping
