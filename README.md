# Ontology-Driven Geological QA System

A Flask-based Geological Ontology Question Answering System that enables users to query geological knowledge using natural language.
This project, Ontology-Driven QA, demonstrates a question-answering system for Geological ontology. It includes Python scripts, front-end templates, and deployment instructions for a complete solution. This system enables users to query geological knowledge using natural language.

## Table of contents

1. [Overview](#overview)
2. [Features](#features)
3. [Technical Architecture](#technical-architecture)
   - [Tools & Technologies](#tools--technologies)
   - [Pipeline Overview](#pipeline-overview)
4. [How to Use](#how-to-use)
5. [Results](#results)
6. [Future Work](#future-work)

## Overview

This project, Ontology-Driven QA, demonstrates a question-answering system for geological ontologies. It integrates Flask as a lightweight web framework, enabling users to query geological knowledge using natural language through a simple and intuitive web interface.

By dynamically extracting and processing geological ontology structures containing over 1600 axioms, this system efficiently answers user queries with relevant results using SPARQL and NLP-powered term matching.

## Features

- Flask Web Interface: A user-friendly web application that allows users to input natural language queries and retrieve geological knowledge seamlessly.

- Ontology-Driven QA: Supports querying complex geological relationships and descriptions from RDF/OWL files using SPARQL.

- Dynamic Ontology Processing: Extracts ontology classes, relationships, and descriptions dynamically for maximum flexibility.

- NLP Integration: Preprocesses and matches user queries with ontology terms using spaCy and PhraseMatcher.

- Efficient Query Optimization: Caches frequently queried data and implements preprocessing to reduce SPARQL execution times.

## Technical Architecture

### Tools & Technologies

- Flask: For building the web interface and deploying the application.
- Python: Core programming language for ontology extraction and query processing.
- RDFLib: Parsing and querying RDF graphs using SPARQL.
- spaCy: NLP pipeline for preprocessing and term matching.
- SPARQL: For retrieving geological knowledge from the ontology.

### Pipeline Overview

- Flask Web Application

  - A responsive interface where users can input natural language queries to retrieve geological insights.

- Ontology Parsing

  - Dynamically parses RDF/OWL ontology files to extract classes, relationships, and instance descriptions.

- NLP Preprocessing

  - Preprocesses user queries and ontology terms using lemmatization and tokenization to improve accuracy.

- SPARQL Query Execution

  - Matches processed queries to ontology terms and retrieves relevant knowledge using SPARQL queries.

- Efficient Query Optimization
  - Reduces initialization and query processing times using caching and multi-threaded processing.

## How to Use

You can access the applictaion using this [Geological Ontology Question Answering System](https://ontology-driven-qa.onrender.com/ "Geological Ontology Question Answering System") or https://ontology-driven-qa.onrender.com/.

## Results

- Built a Flask-based geological QA system that handles natural language queries and retrieves relevant ontology knowledge.
- Extracted and structured 1600+ axioms dynamically from an RDF-based ontology.
- Reduced query initialization times by up to 50% using multi-threading and efficient caching.
- Designed a reusable, scalable framework suitable for any domain-specific ontology.

## Future Work

- Add support for more complex queries involving multiple relationships.
- Develop a dashboard visualization for the query results.
- Experiment with other advanced NLP models.
- Extend support to handle multiple ontologies in parallel.
