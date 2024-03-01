import os
import logging
import json
from flask import Flask, request, jsonify
from pinecone import Pinecone, PodSpec
from langchain_openai import OpenAIEmbeddings, OpenAI as llopenai
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain, LLMChain
from langchain import PromptTemplate

# Initialize logging
logging.basicConfig(level=logging.INFO)

def init_db(app):
    """Initializes the database and related components."""
    try:
        logging.info("Initializing database and related components...")
        app.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        app.pc_index_name = os.getenv("PINECONE_INDEX_NAME")
        app.embeddings = OpenAIEmbeddings()

        if app.pc_index_name not in app.pc.list_indexes().names():
            logging.info("Creating Pinecone index...")
            app.pc.create_index(app.pc_index_name, dimension=1536, metric="cosine", spec=PodSpec(environment="gcp-starter"))

            loader = DirectoryLoader("./data", glob="./*.pdf", loader_cls=PyPDFLoader)
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            documents = text_splitter.split_documents(documents)
            LangchainPinecone.from_documents(documents, app.embeddings, index_name=app.pc_index_name)

        app.vectorstore = LangchainPinecone.from_existing_index(app.pc_index_name, app.embeddings)
        app.llm = llopenai()
        app.qa_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
            llm=app.llm,
            chain_type="stuff",
            retriever=app.vectorstore.as_retriever(),
            return_source_documents=True
        )
        logging.info("Initialization completed successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize the application: {e}")

def document_to_dict(doc):
    # Convert a Document object to a dictionary
    return {
        'page_content': doc.page_content,
        'metadata': doc.metadata
    }

def serialize(value):
    # Initialize a dictionary for the serialized value
    serialized_value = {}

    if isinstance(value, str):
        serialized_value["feedback"] = value
    else:
        # Dynamically serialize each key in the input value
        for key, val in value.items():
            # Apply custom serialization for known complex types
            if key == 'source_documents' and isinstance(val, list):
                serialized_value[key] = [document_to_dict(doc) for doc in val]
            else:
                # For all other values, copy them directly
                serialized_value[key] = val

    return serialized_value

def create_app():
    app = Flask(__name__)

    with app.app_context():
        init_db(app)

    @app.route('/chat', methods=['POST'])
    def chat():
        data = request.json
        message = data.get('message')
        if not message:
            return jsonify({"error": "Message is required"}), 400

        template = "Respond as a teaching assistant, ensuring your reply is structured and conveyed with a professional tone. QUESTION: {question}"
        filled_template = template.format(question=message)
        response_message = app.qa_with_sources.invoke(filled_template)
        return jsonify(serialize(response_message))

    @app.route('/mark', methods=['POST'])
    def mark():
        data = request.json
        message = data.get('message')
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        subject, essay = message.split(':', 1)
        # Constructing the prompt
        prompt_text = """
        Essay Subject: {subject}
        Essay Text: {essay}

        As an expert reviewer, please evaluate the essay based on the following criteria, rating each from 0 to 10, and provide brief feedback:
        1. Content and Understanding: Relevance and depth of the essay in relation to the subject.
        2. Organization and Structure: Clarity and logical flow of ideas.
        3. Style and Tone: Appropriateness and engagement of the writing style and tone.
        4. Grammar and Mechanics: Correctness of grammar and punctuation.
        5. Originality and Creativity: Originality of ideas and creative presentation.

        Provide a summary score for each criterion followed by overall feedback.
        """

        prompt = PromptTemplate(input_variables=["subject", "essay"],template=prompt_text)

        response_message = app.llm.invoke(prompt.format(
        subject=subject,
        essay=essay
        ))
        
        # Serialize response_message appropriately before returning
        # Assuming serialize is a function you have defined to convert the response into a JSON-serializable format
        return jsonify(serialize(response_message))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001)
