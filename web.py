# # app.py (final)
# import os, hashlib, json
# from pathlib import Path

# import streamlit as st
# from dotenv import load_dotenv
# from PyPDF2 import PdfReader
# from langchain.text_splitter import CharacterTextSplitter
# # from langchain.embeddings.openai import OpenAIEmbeddings
# # from langchain.vectorstores.faiss import FAISS
# # from langchain.chat_models import ChatOpenAI
# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain_community.chat_models import ChatOpenAI
# from langchain.memory import ConversationSummaryMemory
# from langchain.chains import ConversationalRetrievalChain


# from htmlTemplates import css, bot_template, user_template

# # CONFIG
# load_dotenv()
# BASE_DIR   = Path(os.getenv("APP_BASE", ".")) 
# STORAGE    = BASE_DIR / "storage"
# INDEX_DIR  = STORAGE / "faiss_index"
# CACHE_FILE = STORAGE / "hash.json"
# EMBED_MODEL= os.getenv("EMBED_MODEL", "text-embedding-ada-002")
# LLM_MODEL  = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

# def ensure_dirs():
#     INDEX_DIR.mkdir(parents=True, exist_ok=True)

# def compute_hash(files):
#     h = hashlib.md5()
#     for f in sorted(files, key=lambda x: x.name):
#         h.update(f.name.encode())
#         h.update(f.read())
#     return h.hexdigest()

# def load_cache():
#     if CACHE_FILE.exists():
#         return json.loads(CACHE_FILE.read_text())
#     return {}

# def update_cache(hash_):
#     CACHE_FILE.write_text(json.dumps({"last_hash": hash_}))

# def get_pdf_text(files):
#     text=""
#     for f in files:
#         try:
#             rdr=PdfReader(f)
#             for p in rdr.pages:
#                 text+=p.extract_text() or ""
#         except Exception as e:
#             st.error(f"Error reading {f.name}: {e}")
#     return text

# # def get_chunks(text):
# #     splitter = CharacterTextSplitter("\n", 1000, 200, len)
# #     return splitter.split_text(text)

# def get_chunks(text):
#     splitter = CharacterTextSplitter(
#         separator="\n",
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len
#     )
#     return splitter.split_text(text)

# def build_or_load_index(chunks, force=False):
#     ensure_dirs()
#     cache = load_cache()
#     curr_hash = compute_hash(st.session_state.pdfs)
#     if not force and cache.get("last_hash")==curr_hash and INDEX_DIR.exists():
#         emb = OpenAIEmbeddings(model=EMBED_MODEL)
#         return FAISS.load_local(str(INDEX_DIR), emb)
#     # else build new
#     emb = OpenAIEmbeddings(model=EMBED_MODEL)
#     vs  = FAISS.from_texts(chunks, emb, metadatas=[{"source": i//1} for i in range(len(chunks))])
#     vs.save_local(str(INDEX_DIR))
#     update_cache(curr_hash)
#     return vs

# def make_chain(vs):
#     llm = ChatOpenAI(model_name=LLM_MODEL, temperature=0)
#     retriever = vs.as_retriever(search_type="mmr", search_kwargs={"k":3,"fetch_k":10})
#     # Summarize old context to bound memory size
#     memory = ConversationSummaryMemory(llm=llm, max_token_limit=1000)
#     return ConversationalRetrievalChain.from_llm(llm, retriever, memory=memory)

# def main():
#     st.set_page_config("Chat with PDFs", ":books:")
#     st.write(css, unsafe_allow_html=True)

#     st.session_state.setdefault("chain", None)
#     st.session_state.setdefault("history", [])
#     st.session_state.setdefault("pdfs", [])

#     with st.sidebar:
#         st.subheader("📂 Documents")
#         uploaded = st.file_uploader("Upload PDFs", accept_multiple_files=True, type="pdf")
#         if uploaded:
#             st.session_state.pdfs = uploaded

#         if st.button("Process"):
#             if not st.session_state.pdfs:
#                 st.warning("Upload PDFs first.")
#             else:
#                 txt = get_pdf_text(st.session_state.pdfs)
#                 chunks = get_chunks(txt)
#                 st.info(f"🔖 {len(chunks)} chunks created.")
#                 vs = build_or_load_index(chunks)
#                 st.session_state.chain = make_chain(vs)

#         if st.button("Clear Chat"):
#             st.session_state.chain = None
#             st.session_state.history.clear()

#     st.header("💬 Ask your documents")
#     if not st.session_state.chain:
#         st.info("Process your PDFs to start.")
#         return

#     # q = st.text_input("Your question:")
#     # if q:
#     #     # try:
#     #     #     resp = st.session_state.chain({"question": q})
#     #     #     st.session_state.history = resp["chat_history"]
#     #     try:
#     #         resp = st.session_state.chain({
#     #             "question": q,
#     #             "chat_history": st.session_state.history
#     #         })
#     #         resp = st.session_state.chain({"question": q})
#     #         st.session_state.history = resp["chat_history"]
#     #     except Exception as e:
#     #         st.error(f"LLM error: {e}")
#     q = st.text_input("Your question:")
#     if q and st.session_state.chain:
#         try:
#             # Build the payload dynamically
#             payload = {}
#             keys = st.session_state.chain.input_keys  # what the chain wants
#             if "question" in keys:
#                 payload["question"] = q
#             if "chat_history" in keys:
#                 payload["chat_history"] = st.session_state.history or []

#             # Call the chain with exactly the keys it expects
#             resp = st.session_state.chain(payload)
#             st.session_state.history = resp["chat_history"]
#         except Exception as e:
#             st.error(f"LLM error: {e}")

#     for i, m in enumerate(st.session_state.history):
#         tpl = user_template if i % 2 == 0 else bot_template
#         st.write(tpl.replace("{{MSG}}", m.content), unsafe_allow_html=True)

#     if st.session_state.history:
#         txt = "\n\n".join(f"{m.role}: {m.content}" for m in st.session_state.history)
#         st.download_button("📥 Download Transcript", txt, "chat.txt")

# if __name__=="__main__":
#     main()

































# import streamlit as st
# from dotenv import load_dotenv
# import os
# import json
# import hashlib
# from PyPDF2 import PdfReader
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain_community.chat_models import ChatOpenAI
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationalRetrievalChain
# from langchain_core.messages import HumanMessage, AIMessage
# from langchain_core.documents import Document # Import Document for richer chunk metadata

# # --- Configuration ---
# STORAGE_ROOT = "C:\\Users\\debab\\Desktop\\IIT+SELF LEARNING\\CODING\\CHAT BOTS\\Chat with Multiple PDFs\\storage"
# os.makedirs(STORAGE_ROOT, exist_ok=True) # Ensure root storage directory exists

# # --- Helper Functions ---

# def get_pdf_documents_with_metadata(pdf_docs):
#     """
#     Extracts text from PDFs and returns a list of Langchain Document objects,
#     each with metadata for source (filename) and page number.
#     """
#     documents = []
#     for pdf in pdf_docs:
#         try:
#             pdf_reader = PdfReader(pdf)
#             for i, page in enumerate(pdf_reader.pages):
#                 page_text = page.extract_text()
#                 if page_text:
#                     documents.append(Document(
#                         page_content=page_text,
#                         metadata={"source": pdf.name, "page": i + 1}
#                     ))
#                 else:
#                     st.warning(f"Could not extract text from page {i+1} in '{pdf.name}'. This page might be an image or scanned.")
#         except Exception as e:
#             st.error(f"Error reading PDF '{pdf.name}'. It might be corrupted or password-protected. Error: {e}")
#             return None # Indicate an error for the batch

#     if not documents:
#         st.warning("No text could be extracted from the uploaded PDFs.")
#         return None
#     return documents

# def get_text_chunks(documents):
#     """
#     Splits a list of Langchain Document objects into smaller chunks, preserving metadata.
#     """
#     text_splitter = CharacterTextSplitter(
#         separator="\n",
#         chunk_size=1000,
#         chunk_overlap=200,
#         length_function=len
#     )
#     chunks = text_splitter.split_documents(documents) # Use split_documents for Document objects
#     return chunks

# @st.cache_resource(show_spinner=False)
# def get_embeddings_model():
#     """Caches and returns the OpenAIEmbeddings model."""
#     try:
#         return OpenAIEmbeddings()
#     except Exception as e:
#         st.error(f"Failed to initialize OpenAI Embeddings. Please check your OPENAI_API_KEY. Error: {e}")
#         return None

# def get_vectorstore(text_chunks, existing_vectorstore=None):
#     """
#     Creates a new FAISS vector store or adds chunks to an existing one.
#     """
#     embeddings = get_embeddings_model()
#     if embeddings is None:
#         return None

#     try:
#         if existing_vectorstore:
#             st.text("Adding new documents to existing vector store...")
#             existing_vectorstore.add_documents(documents=text_chunks) # Use add_documents for Document objects
#             return existing_vectorstore
#         else:
#             st.text("Creating new vector store and embeddings...")
#             vectorstore = FAISS.from_documents(documents=text_chunks, embedding=embeddings) # Use from_documents
#             return vectorstore
#     except Exception as e:
#         st.error(f"Error creating/updating vector store: {e}")
#         return None

# def get_conversation_chain(vectorstore, chat_history_messages=[]):
#     """
#     Initializes or updates the conversational retrieval chain.
#     Populates memory with provided chat_history_messages.
#     """
#     if vectorstore is None:
#         return None
#     try:
#         llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
#         memory = ConversationBufferMemory(
#             memory_key='chat_history', return_messages=True)

#         # Manually populate the memory with the loaded chat history
#         for msg in chat_history_messages:
#             if isinstance(msg, HumanMessage):
#                 memory.chat_memory.add_user_message(msg.content)
#             elif isinstance(msg, AIMessage):
#                 memory.chat_memory.add_ai_message(msg.content)

#         conversation_chain = ConversationalRetrievalChain.from_llm(
#             llm=llm,
#             retriever=vectorstore.as_retriever(search_kwargs={"k": 5}), # Retrieve top 5 relevant chunks
#             memory=memory
#         )
#         return conversation_chain
#     except Exception as e:
#         st.error(f"Error initializing conversation chain: {e}")
#         return None

# def generate_document_set_id(pdf_names):
#     """Generates a unique ID for a set of documents based on their sorted names."""
#     if not pdf_names:
#         return "default_documents"
#     sorted_names = sorted([name for name in pdf_names])
#     return hashlib.md5("".join(sorted_names).encode()).hexdigest()

# def get_document_set_path(doc_set_id):
#     return os.path.join(STORAGE_ROOT, doc_set_id)

# def get_faiss_index_path(doc_set_id):
#     return os.path.join(get_document_set_path(doc_set_id), "faiss_index")

# def get_chat_history_file_path(doc_set_id):
#     return os.path.join(get_document_set_path(doc_set_id), "chat_history.json")

# def load_document_set_metadata():
#     metadata_path = os.path.join(STORAGE_ROOT, "document_sets_metadata.json")
#     if os.path.exists(metadata_path):
#         try:
#             with open(metadata_path, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except json.JSONDecodeError:
#             st.warning("Document sets metadata file is corrupted. Starting fresh.")
#             return {}
#     return {}

# def save_document_set_metadata(metadata):
#     metadata_path = os.path.join(STORAGE_ROOT, "document_sets_metadata.json")
#     try:
#         with open(metadata_path, 'w', encoding='utf-8') as f:
#             json.dump(metadata, f, ensure_ascii=False, indent=4)
#     except Exception as e:
#         st.error(f"Error saving document set metadata: {e}")

# def load_chat_history(doc_set_id):
#     history_path = get_chat_history_file_path(doc_set_id)
#     if os.path.exists(history_path):
#         try:
#             with open(history_path, 'r', encoding='utf-8') as f:
#                 raw_history = json.load(f)
#                 messages = []
#                 for msg in raw_history:
#                     if msg["type"] == "human":
#                         messages.append(HumanMessage(content=msg["content"]))
#                     elif msg["type"] == "ai":
#                         messages.append(AIMessage(content=msg["content"]))
#                 return messages
#         except json.JSONDecodeError:
#             st.warning(f"Chat history for '{doc_set_id}' is corrupted. Starting with an empty history.")
#             return []
#         except Exception as e:
#             st.error(f"Error loading chat history for '{doc_set_id}': {e}")
#             return []
#     return []

# def save_chat_history(chat_history_messages, doc_set_id):
#     history_path = get_chat_history_file_path(doc_set_id)
#     os.makedirs(os.path.dirname(history_path), exist_ok=True)
#     try:
#         serializable_history = []
#         for msg in chat_history_messages:
#             serializable_history.append({"type": msg.type, "content": msg.content})

#         with open(history_path, 'w', encoding='utf-8') as f:
#             json.dump(serializable_history, f, ensure_ascii=False, indent=4)
#     except Exception as e:
#         st.error(f"Error saving chat history for '{doc_set_id}': {e}")

# def display_chat_message(message_content, is_user):
#     # Simple styling using Streamlit's markdown with HTML
#     if is_user:
#         st.markdown(f'<div style="background-color:#e6f7ff; color:#333333; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #007bff;"><strong>You:</strong> {message_content}</div>', unsafe_allow_html=True)
#     else:
#         st.markdown(f'<div style="background-color:#f0f0f0; color:#333333; padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 5px solid #6c757d;"><strong>Bot:</strong> {message_content}</div>', unsafe_allow_html=True)



# def handle_userinput(user_question):
#     if st.session_state.conversation is None:
#         st.warning("Please process or load your documents first to start a conversation!")
#         return

#     try:
#         response = st.session_state.conversation({'question': user_question})

#         st.session_state.chat_history.append(HumanMessage(content=user_question))
#         st.session_state.chat_history.append(AIMessage(content=response['answer']))

#         # Display full chat history
#         for message in st.session_state.chat_history:
#             if isinstance(message, HumanMessage):
#                 display_chat_message(message.content, True)
#             elif isinstance(message, AIMessage):
#                 display_chat_message(message.content, False)

#         # Display source documents separately
#         if 'source_documents' in response and response['source_documents']:
#             with st.expander("Show Source Documents"):
#                 for i, doc in enumerate(response['source_documents']):
#                     source_name = doc.metadata.get('source', 'Unknown Document')
#                     page_number = doc.metadata.get('page', 'N/A')
#                     st.markdown(f"**Source {i+1}:** `{source_name}` (Page: {page_number})")
#                     # Display first 500 characters of the content
#                     st.text(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))
#                     st.markdown("---")

#         save_chat_history(st.session_state.chat_history, st.session_state.current_doc_set_id)

#     except Exception as e:
#         st.error(f"Error handling user input: {e}")


# def main():
#     load_dotenv()
#     st.set_page_config(page_title="Chat with Multiple PDFs", page_icon=":books:", layout="wide")

#     # --- Session State Initialization ---
#     if "conversation" not in st.session_state:
#         st.session_state.conversation = None
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []
#     if "vectorstore" not in st.session_state:
#         st.session_state.vectorstore = None
#     if "current_doc_set_id" not in st.session_state:
#         st.session_state.current_doc_set_id = "default_documents" # Default set
#     if "doc_sets_metadata" not in st.session_state:
#         st.session_state.doc_sets_metadata = load_document_set_metadata()
#         # Ensure 'default_documents' entry exists
#         if "default_documents" not in st.session_state.doc_sets_metadata:
#             st.session_state.doc_sets_metadata["default_documents"] = {
#                 "name": "Default Documents",
#                 "files": [],
#                 "faiss_path": get_faiss_index_path("default_documents"),
#                 "chat_history_path": get_chat_history_file_path("default_documents")
#             }
#             save_document_set_metadata(st.session_state.doc_sets_metadata)

#     # Load initial chat history for the current document set
#     # This must happen before get_conversation_chain to ensure memory is populated
#     st.session_state.chat_history = load_chat_history(st.session_state.current_doc_set_id)

#     # Re-initialize conversation chain if vectorstore is already loaded for current set
#     if st.session_state.vectorstore is None and \
#        st.session_state.current_doc_set_id in st.session_state.doc_sets_metadata:
#         faiss_path = get_faiss_index_path(st.session_state.current_doc_set_id)
#         if os.path.exists(faiss_path) and len(os.listdir(faiss_path)) > 0:
#             try:
#                 embeddings = get_embeddings_model()
#                 if embeddings:
#                     st.session_state.vectorstore = FAISS.load_local(
#                         faiss_path,
#                         embeddings,
#                         allow_dangerous_deserialization=True
#                     )
#                     st.session_state.conversation = get_conversation_chain(
#                         st.session_state.vectorstore,
#                         st.session_state.chat_history # Pass loaded history
#                     )
#                     st.success(f"Automatically loaded '{st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]['name']}' on startup.")
#             except Exception as e:
#                 st.warning(f"Could not auto-load default or last active document set. Error: {e}")
#                 st.session_state.vectorstore = None
#                 st.session_state.conversation = None
#                 st.session_state.current_doc_set_id = "default_documents"
#                 st.session_state.chat_history = [] # Reset history if load fails

#     st.markdown("<h1 style='text-align: center;'>Chat with Multiple PDFs :books:</h1>", unsafe_allow_html=True)
#     st.markdown("<hr/>", unsafe_allow_html=True)

#     # --- Main Chat Area ---
#     chat_container = st.container()
#     with chat_container:
#         for message in st.session_state.chat_history:
#             if isinstance(message, HumanMessage):
#                 display_chat_message(message.content, True)
#             elif isinstance(message, AIMessage):
#                 display_chat_message(message.content, False)

#     user_question = st.text_input("Ask a question about your documents:", key="user_question_input", placeholder="Type your question here...", disabled=(st.session_state.conversation is None))
#     if user_question:
#         handle_userinput(user_question)
    
#     st.markdown("---") # Separator

#     col1, col2 = st.columns([1, 1])

#     with col1:
#         if st.button("Clear Current Chat", key="clear_chat_button"):
#             st.session_state.chat_history = []
#             save_chat_history([], st.session_state.current_doc_set_id)
#             # Re-initiate conversation chain to clear its internal memory
#             st.session_state.conversation = get_conversation_chain(st.session_state.vectorstore, [])
#             st.experimental_rerun()

#     with col2:
#         if st.session_state.vectorstore:
#             st.success(f"Currently active document set: **{st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]['name']}**")
#         else:
#             st.info("No documents currently loaded.")

#     # --- Sidebar for Document Management ---
#     with st.sidebar:
#         st.subheader("Document Management")

#         # Display files in current active set
#         if st.session_state.current_doc_set_id in st.session_state.doc_sets_metadata:
#             current_set_name = st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]['name']
#             current_set_files = st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]['files']
#             st.markdown(f"**Current Set: {current_set_name}**")
#             if current_set_files:
#                 for f_name in current_set_files:
#                     st.markdown(f"- {f_name}")
#             else:
#                 st.info("No files in this set yet. Upload new PDFs to add.")
#             st.markdown("---")

#         # --- Upload and Process New/Add Documents ---
#         st.markdown("#### Upload & Process PDFs")
#         pdf_docs = st.file_uploader(
#             "Upload new PDFs here", accept_multiple_files=True, key="pdf_uploader"
#         )
        
#         process_option = st.radio(
#             "Choose processing option:",
#             ("Create New Document Set", "Add to Current Document Set"),
#             key="process_option_radio",
#             disabled=(not pdf_docs) # Disable if no PDFs uploaded
#         )

#         # Dynamic name input
#         new_doc_set_name_default = ""
#         if pdf_docs:
#             uploaded_pdf_names = [pdf.name for pdf in pdf_docs]
#             new_doc_set_name_default = f"Documents_{'_'.join(name.replace('.pdf', '') for name in uploaded_pdf_names[:2])}{'...' if len(uploaded_pdf_names) > 2 else ''}"
        
#         new_doc_set_name = st.text_input("Name for the new document set (optional):", value=new_doc_set_name_default, key="new_set_name_input", disabled=(process_option != "Create New Document Set"))


#         if st.button("Process Documents", key="process_button"):
#             if not pdf_docs:
#                 st.warning("Please upload at least one PDF document to process.")
#                 return

#             if process_option == "Add to Current Document Set" and not st.session_state.vectorstore:
#                 st.warning("No active document set to add to. Please 'Create New Document Set' first or load an existing one.")
#                 return

#             uploaded_pdf_names = [pdf.name for pdf in pdf_docs]
#             # Use a more robust ID based on the *actual content* of the files, or combine with current set ID
#             # For simplicity and consistency with previous design, we stick to hash of names for new sets
#             # For "Add to current", the ID is simply the current_doc_set_id
            
#             if process_option == "Create New Document Set":
#                 doc_set_id_to_process = generate_document_set_id(uploaded_pdf_names)
                
#                 # Check if this exact set of files already exists
#                 if doc_set_id_to_process in st.session_state.doc_sets_metadata:
#                     st.info("A document set with these exact files already exists. Loading it instead of reprocessing.")
#                     st.session_state.current_doc_set_id = doc_set_id_to_process
#                     # Load existing vectorstore
#                     with st.spinner("Loading existing vector store..."):
#                         try:
#                             embeddings = get_embeddings_model()
#                             if not embeddings: return
#                             loaded_vectorstore = FAISS.load_local(
#                                 get_faiss_index_path(doc_set_id_to_process),
#                                 embeddings,
#                                 allow_dangerous_deserialization=True
#                             )
#                             st.session_state.vectorstore = loaded_vectorstore
#                             st.session_state.chat_history = load_chat_history(doc_set_id_to_process)
#                             st.session_state.conversation = get_conversation_chain(loaded_vectorstore, st.session_state.chat_history)
#                             st.success(f"Loaded existing document set: {st.session_state.doc_sets_metadata[doc_set_id_to_process]['name']}")
#                             st.experimental_rerun()
#                         except Exception as e:
#                             st.error(f"Error loading existing vector store: {e}")
#                             st.session_state.vectorstore = None
#                             st.session_state.conversation = None
#                             st.session_state.chat_history = [] # Clear history on error
#                     return
                
#                 with st.spinner("Processing new documents and creating new set..."):
#                     # Get documents with metadata
#                     documents = get_pdf_documents_with_metadata(pdf_docs)
#                     if documents is None: return

#                     st.text("Splitting text into chunks...")
#                     text_chunks = get_text_chunks(documents)

#                     vectorstore = get_vectorstore(text_chunks)
#                     if vectorstore is None: return

#                     # Save new FAISS index
#                     faiss_save_path = get_faiss_index_path(doc_set_id_to_process)
#                     os.makedirs(faiss_save_path, exist_ok=True)
#                     try:
#                         vectorstore.save_local(faiss_save_path)
#                         st.success("Vector store processed and saved!")
#                     except Exception as e:
#                         st.error(f"Error saving vector store: {e}")
#                         return
                    
#                     # Update metadata and session state
#                     final_set_name = new_doc_set_name if new_doc_set_name else f"Documents_{doc_set_id_to_process[:6]}"
#                     st.session_state.doc_sets_metadata[doc_set_id_to_process] = {
#                         "name": final_set_name,
#                         "files": uploaded_pdf_names,
#                         "faiss_path": faiss_save_path,
#                         "chat_history_path": get_chat_history_file_path(doc_set_id_to_process)
#                     }
#                     save_document_set_metadata(st.session_state.doc_sets_metadata)
#                     st.session_state.current_doc_set_id = doc_set_id_to_process
#                     st.session_state.vectorstore = vectorstore
#                     st.session_state.chat_history = [] # New set, new history
#                     save_chat_history([], doc_set_id_to_process)
#                     st.session_state.conversation = get_conversation_chain(vectorstore, []) # Re-initiate chain with empty history
#                     st.success(f"'{final_set_name}' created and loaded!")
#                     st.experimental_rerun() # Refresh UI
                    
#             elif process_option == "Add to Current Document Set":
#                 current_doc_set_id = st.session_state.current_doc_set_id
#                 current_doc_set_name = st.session_state.doc_sets_metadata[current_doc_set_id]['name']

#                 with st.spinner(f"Adding documents to '{current_doc_set_name}'..."):
#                     # Get documents with metadata
#                     documents = get_pdf_documents_with_metadata(pdf_docs)
#                     if documents is None: return

#                     st.text("Splitting text into chunks...")
#                     text_chunks = get_text_chunks(documents)

#                     # Add to existing vector store
#                     updated_vectorstore = get_vectorstore(text_chunks, st.session_state.vectorstore)
#                     if updated_vectorstore is None: return

#                     # Save updated FAISS index
#                     faiss_save_path = get_faiss_index_path(current_doc_set_id)
#                     try:
#                         updated_vectorstore.save_local(faiss_save_path)
#                         st.success("Documents added and vector store updated!")
#                     except Exception as e:
#                         st.error(f"Error saving updated vector store: {e}")
#                         return
                    
#                     # Update metadata with new files
#                     existing_files = st.session_state.doc_sets_metadata[current_doc_set_id]["files"]
#                     new_unique_files = list(set(existing_files + uploaded_pdf_names)) # Add unique new files
#                     st.session_state.doc_sets_metadata[current_doc_set_id]["files"] = new_unique_files
#                     save_document_set_metadata(st.session_state.doc_sets_metadata)
                    
#                     st.session_state.vectorstore = updated_vectorstore
#                     # Re-initiate conversation chain with the updated vectorstore and current chat history
#                     st.session_state.conversation = get_conversation_chain(updated_vectorstore, st.session_state.chat_history)
#                     st.success(f"Documents successfully added to '{current_doc_set_name}'!")
#                     st.experimental_rerun() # Refresh UI

#         st.markdown("---")

#         # --- Load Existing Document Sets ---
#         st.markdown("#### Load Saved Document Sets")
        
#         available_doc_sets = {
#             metadata["name"]: doc_id
#             for doc_id, metadata in st.session_state.doc_sets_metadata.items()
#             if os.path.exists(get_faiss_index_path(doc_id)) and os.listdir(get_faiss_index_path(doc_id)) # Check if directory exists and is not empty
#         }

#         if available_doc_sets:
#             current_selected_index = 0
#             if st.session_state.current_doc_set_id in st.session_state.doc_sets_metadata:
#                 current_active_set_name = st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]["name"]
#                 if current_active_set_name in available_doc_sets:
#                     current_selected_index = list(available_doc_sets.keys()).index(current_active_set_name)

#             selected_doc_set_name = st.selectbox(
#                 "Select a saved document set:",
#                 options=list(available_doc_sets.keys()),
#                 index=current_selected_index,
#                 key="select_doc_set"
#             )
            
#             selected_doc_set_id = available_doc_sets[selected_doc_set_name]

#             if st.button("Load Selected Set", key="load_set_button"):
#                 if st.session_state.current_doc_set_id == selected_doc_set_id:
#                     st.info(f"'{selected_doc_set_name}' is already the active document set.")
#                     return

#                 with st.spinner(f"Loading '{selected_doc_set_name}'..."):
#                     try:
#                         embeddings = get_embeddings_model()
#                         if not embeddings: return
#                         loaded_vectorstore = FAISS.load_local(
#                             get_faiss_index_path(selected_doc_set_id),
#                             embeddings,
#                             allow_dangerous_deserialization=True
#                         )
#                         st.session_state.vectorstore = loaded_vectorstore
#                         st.session_state.current_doc_set_id = selected_doc_set_id
#                         st.session_state.chat_history = load_chat_history(selected_doc_set_id)
#                         st.session_state.conversation = get_conversation_chain(loaded_vectorstore, st.session_state.chat_history)
#                         st.success(f"'{selected_doc_set_name}' loaded successfully!")
#                         st.experimental_rerun()
#                     except Exception as e:
#                         st.error(f"Error loading saved vector store for '{selected_doc_set_name}': {e}")
#                         st.session_state.vectorstore = None
#                         st.session_state.conversation = None
#                         st.session_state.current_doc_set_id = "default_documents" # Fallback
#                         st.session_state.chat_history = load_chat_history("default_documents") # Load default history if fallback

#         else:
#             st.info("No saved document sets found.")

#         st.markdown("---")
#         st.markdown("#### Delete Document Set")
        
#         # Only show document sets that actually have a folder to delete
#         delete_doc_sets_options = {
#             metadata["name"]: doc_id
#             for doc_id, metadata in st.session_state.doc_sets_metadata.items()
#             if os.path.exists(get_document_set_path(doc_id))
#         }
        
#         if delete_doc_sets_options:
#             selected_delete_set_name = st.selectbox(
#                 "Select set to delete:",
#                 options=list(delete_doc_sets_options.keys()),
#                 key="select_delete_set"
#             )
            
#             delete_id = delete_doc_sets_options[selected_delete_set_name]

#             # Confirmation checkbox for deletion
#             confirm_delete = st.checkbox(f"Are you sure you want to delete '{selected_delete_set_name}' and all its data (including history)?", key="confirm_delete_checkbox")

#             if st.button("Delete Selected Set", key="delete_set_button", disabled=not confirm_delete):
#                 if delete_id == st.session_state.current_doc_set_id:
#                     st.warning("Cannot delete the currently active document set. Please switch to another set (or process new documents to create a new active set) before deleting this one.")
#                 else:
#                     with st.spinner(f"Deleting '{selected_delete_set_name}'..."):
#                         try:
#                             import shutil
#                             shutil.rmtree(get_document_set_path(delete_id))
#                             del st.session_state.doc_sets_metadata[delete_id]
#                             save_document_set_metadata(st.session_state.doc_sets_metadata)
#                             st.success(f"'{selected_delete_set_name}' deleted successfully!")
#                             st.experimental_rerun() # Refresh UI to remove deleted set from options
#                         except Exception as e:
#                             st.error(f"Error deleting set: {e}")
#         else:
#             st.info("No document sets to delete.")

# if __name__ == '__main__':
#     main()

























import streamlit as st
from dotenv import load_dotenv
import os
import json
import hashlib
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document

# --- Configuration ---
STORAGE_ROOT = "C:\\Users\\debab\\Desktop\\IIT+SELF LEARNING\\CODING\\CHAT BOTS\\Chat with Multiple PDFs\\storage"
os.makedirs(STORAGE_ROOT, exist_ok=True) # Ensure root storage directory exists

# --- Helper Functions (No changes to these unless specified below) ---

def get_pdf_documents_with_metadata(pdf_docs):
    """
    Extracts text from PDFs and returns a list of Langchain Document objects,
    each with metadata for source (filename) and page number.
    """
    documents = []
    for pdf in pdf_docs:
        try:
            pdf_reader = PdfReader(pdf)
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    documents.append(Document(
                        page_content=page_text,
                        metadata={"source": pdf.name, "page": i + 1}
                    ))
                else:
                    st.warning(f"Could not extract text from page {i+1} in '{pdf.name}'. This page might be an image or scanned.")
        except Exception as e:
            st.error(f"Error reading PDF '{pdf.name}'. It might be corrupted or password-protected. Error: {e}")
            return None # Indicate an error for the batch

    if not documents:
        st.warning("No text could be extracted from the uploaded PDFs.")
        return None
    return documents

def get_text_chunks(documents):
    """
    Splits a list of Langchain Document objects into smaller chunks, preserving metadata.
    """
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents) # Use split_documents for Document objects
    return chunks

@st.cache_resource(show_spinner=False)
def get_embeddings_model():
    """Caches and returns the OpenAIEmbeddings model."""
    try:
        return OpenAIEmbeddings()
    except Exception as e:
        st.error(f"Failed to initialize OpenAI Embeddings. Please check your OPENAI_API_KEY. Error: {e}")
        return None

def get_vectorstore(text_chunks, existing_vectorstore=None):
    """
    Creates a new FAISS vector store or adds chunks to an existing one.
    """
    embeddings = get_embeddings_model()
    if embeddings is None:
        return None

    try:
        if existing_vectorstore:
            st.text("Adding new documents to existing vector store...")
            existing_vectorstore.add_documents(documents=text_chunks) # Use add_documents for Document objects
            return existing_vectorstore
        else:
            st.text("Creating new vector store and embeddings...")
            vectorstore = FAISS.from_documents(documents=text_chunks, embedding=embeddings) # Use from_documents
            return vectorstore
    except Exception as e:
        st.error(f"Error creating/updating vector store: {e}")
        return None

def get_conversation_chain(vectorstore, chat_history_messages=[]):
    """
    Initializes or updates the conversational retrieval chain.
    Populates memory with provided chat_history_messages.
    """
    if vectorstore is None:
        return None
    try:
        # llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
        memory = ConversationBufferMemory(
            memory_key='chat_history', return_messages=True)

        # Manually populate the memory with the loaded chat history
        for msg in chat_history_messages:
            if isinstance(msg, HumanMessage):
                memory.chat_memory.add_user_message(msg.content)
            elif isinstance(msg, AIMessage):
                memory.chat_memory.add_ai_message(msg.content)

        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 5}), # Retrieve top 5 relevant chunks
            memory=memory
        )
        return conversation_chain
    except Exception as e:
        st.error(f"Error initializing conversation chain: {e}")
        return None

def generate_document_set_id(pdf_names):
    """Generates a unique ID for a set of documents based on their sorted names."""
    if not pdf_names:
        return "default_documents"
    sorted_names = sorted([name for name in pdf_names])
    return hashlib.md5("".join(sorted_names).encode()).hexdigest()

def get_document_set_path(doc_set_id):
    return os.path.join(STORAGE_ROOT, doc_set_id)

def get_faiss_index_path(doc_set_id):
    return os.path.join(get_document_set_path(doc_set_id), "faiss_index")

def get_chat_history_file_path(doc_set_id):
    return os.path.join(get_document_set_path(doc_set_id), "chat_history.json")

def load_document_set_metadata():
    metadata_path = os.path.join(STORAGE_ROOT, "document_sets_metadata.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.warning("Document sets metadata file is corrupted. Starting fresh.")
            return {}
    return {}

def save_document_set_metadata(metadata):
    metadata_path = os.path.join(STORAGE_ROOT, "document_sets_metadata.json")
    try:
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error saving document set metadata: {e}")

def load_chat_history(doc_set_id):
    history_path = get_chat_history_file_path(doc_set_id)
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                raw_history = json.load(f)
                messages = []
                for msg in raw_history:
                    if msg["type"] == "human":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["type"] == "ai":
                        messages.append(AIMessage(content=msg["content"]))
                return messages
        except json.JSONDecodeError:
            st.warning(f"Chat history for '{doc_set_id}' is corrupted. Starting with an empty history.")
            return []
        except Exception as e:
            st.error(f"Error loading chat history for '{doc_set_id}': {e}")
            return []
    return []

def save_chat_history(chat_history_messages, doc_set_id):
    history_path = get_chat_history_file_path(doc_set_id)
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    try:
        serializable_history = []
        for msg in chat_history_messages:
            serializable_history.append({"type": msg.type, "content": msg.content})

        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Error saving chat history for '{doc_set_id}': {e}")

# --- MODIFIED: Use st.chat_message for display ---
def display_chat_message(message_content, is_user):
    """Displays a chat message using st.chat_message."""
    with st.chat_message("user" if is_user else "ai"):
        st.write(message_content)


def handle_userinput(user_question):
    if st.session_state.conversation is None:
        st.warning("Please process or load your documents first to start a conversation!")
        return

    # Add user question to history immediately
    st.session_state.chat_history.append(HumanMessage(content=user_question))
    save_chat_history(st.session_state.chat_history, st.session_state.current_doc_set_id) # Save history after user input

    # Display user message
    with st.chat_message("user"):
        st.write(user_question)

    try:
        # Get response from LLM
        with st.spinner("Thinking..."): # Show spinner while waiting for LLM
            response = st.session_state.conversation({'question': user_question})

        # Add bot answer to history
        st.session_state.chat_history.append(AIMessage(content=response['answer']))
        save_chat_history(st.session_state.chat_history, st.session_state.current_doc_set_id) # Save history after bot response

        # Display bot message
        with st.chat_message("ai"):
            st.write(response['answer'])

            # Display source documents separately
            if 'source_documents' in response and response['source_documents']:
                with st.expander("Show Source Documents"):
                    for i, doc in enumerate(response['source_documents']):
                        source_name = doc.metadata.get('source', 'Unknown Document')
                        page_number = doc.metadata.get('page', 'N/A')
                        st.markdown(f"**Source {i+1}:** `{source_name}` (Page: {page_number})")
                        # Display first 500 characters of the content
                        st.text(doc.page_content[:500] + ("..." if len(doc.page_content) > 500 else ""))
                        st.markdown("---")

    except Exception as e:
        st.error(f"Error handling user input: {e}")
        st.session_state.chat_history.pop() # Remove user message if bot fails to respond
        save_chat_history(st.session_state.chat_history, st.session_state.current_doc_set_id)


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with Multiple PDFs", page_icon=":books:", layout="wide")

    # --- Session State Initialization ---
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "current_doc_set_id" not in st.session_state:
        st.session_state.current_doc_set_id = "default_documents" # Default set
    if "doc_sets_metadata" not in st.session_state:
        st.session_state.doc_sets_metadata = load_document_set_metadata()
        # Ensure 'default_documents' entry exists
        if "default_documents" not in st.session_state.doc_sets_metadata:
            st.session_state.doc_sets_metadata["default_documents"] = {
                "name": "Default Documents",
                "files": [],
                "faiss_path": get_faiss_index_path("default_documents"),
                "chat_history_path": get_chat_history_file_path("default_documents")
            }
            save_document_set_metadata(st.session_state.doc_sets_metadata)

    # Load initial chat history for the current document set
    st.session_state.chat_history = load_chat_history(st.session_state.current_doc_set_id)

    # Re-initialize conversation chain if vectorstore is already loaded for current set
    if st.session_state.vectorstore is None and \
       st.session_state.current_doc_set_id in st.session_state.doc_sets_metadata:
        faiss_path = get_faiss_index_path(st.session_state.current_doc_set_id)
        if os.path.exists(faiss_path) and os.listdir(faiss_path): # Check if directory exists and is not empty
            try:
                embeddings = get_embeddings_model()
                if embeddings:
                    st.session_state.vectorstore = FAISS.load_local(
                        faiss_path,
                        embeddings,
                        allow_dangerous_deserialization=True
                    )
                    st.session_state.conversation = get_conversation_chain(
                        st.session_state.vectorstore,
                        st.session_state.chat_history # Pass loaded history
                    )
                    st.success(f"Automatically loaded '{st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]['name']}' on startup.")
            except Exception as e:
                st.warning(f"Could not auto-load default or last active document set. Error: {e}")
                st.session_state.vectorstore = None
                st.session_state.conversation = None
                st.session_state.current_doc_set_id = "default_documents"
                st.session_state.chat_history = [] # Reset history if load fails

    st.markdown("<h1 style='text-align: center;'>Chat with Multiple PDFs :books:</h1>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)

    # --- Main Chat Area ---
    chat_messages_container = st.container(height=500) # Fixed height with scrollbar

    with chat_messages_container:
        for message in st.session_state.chat_history:
            display_chat_message(message.content, isinstance(message, HumanMessage))

    # --- MODIFIED: Input and Control Area (fixed at bottom) using st.form ---
    st.markdown("<br/>", unsafe_allow_html=True) # Add some space before input

    with st.form(key="chat_input_form", clear_on_submit=True): # clear_on_submit is key!
        user_question = st.text_input(
            "Ask a question about your documents:",
            placeholder="Type your question here...",
            disabled=(st.session_state.conversation is None),
            key="chat_text_input" # Use a distinct key for the text input itself
        )
        submit_button = st.form_submit_button(label="Send")

        if submit_button and user_question:
            handle_userinput(user_question)
            # st.rerun() is generally not needed here if clear_on_submit=True
            # and the chat history is drawn from session_state as it should be.
            # However, if you notice the message not appearing immediately, a rerun can help.
            # For simplicity, let's include it for immediate redraw.
            st.rerun() # Force a rerun to display new messages

    st.markdown("---") # Separator

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Clear Current Chat", key="clear_chat_button"):
            st.session_state.chat_history = []
            save_chat_history([], st.session_state.current_doc_set_id)
            st.session_state.conversation = get_conversation_chain(st.session_state.vectorstore, [])
            st.rerun() # Force a rerun to clear the display

    with col2:
        if st.session_state.vectorstore:
            st.success(f"Currently active document set: **{st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]['name']}**")
        else:
            st.info("No documents currently loaded.")

    # --- Sidebar for Document Management ---
    with st.sidebar:
        st.subheader("Document Management")

        # Display files in current active set
        if st.session_state.current_doc_set_id in st.session_state.doc_sets_metadata:
            current_set_name = st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]['name']
            current_set_files = st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]['files']
            st.markdown(f"**Current Set: {current_set_name}**")
            if current_set_files:
                for f_name in current_set_files:
                    st.markdown(f"- {f_name}")
            else:
                st.info("No files in this set yet. Upload new PDFs to add.")
            st.markdown("---")

        # --- Upload and Process New/Add Documents ---
        st.markdown("#### Upload & Process PDFs")
        pdf_docs = st.file_uploader(
            "Upload new PDFs here", accept_multiple_files=True, key="pdf_uploader"
        )
        
        process_option = st.radio(
            "Choose processing option:",
            ("Create New Document Set", "Add to Current Document Set"),
            key="process_option_radio",
            disabled=(not pdf_docs) # Disable if no PDFs uploaded
        )

        # Dynamic name input
        new_doc_set_name_default = ""
        if pdf_docs:
            uploaded_pdf_names = [pdf.name for pdf in pdf_docs]
            # Suggest a name based on the first few uploaded files
            new_doc_set_name_default = f"Documents_{'_'.join(name.replace('.pdf', '') for name in uploaded_pdf_names[:2])}{'...' if len(uploaded_pdf_names) > 2 else ''}"
        
        new_doc_set_name = st.text_input("Name for the new document set (optional):", value=new_doc_set_name_default, key="new_set_name_input", disabled=(process_option != "Create New Document Set"))


        if st.button("Process Documents", key="process_button"):
            if not pdf_docs:
                st.warning("Please upload at least one PDF document to process.")
                st.stop() # Stop execution to prevent further processing
            
            if process_option == "Add to Current Document Set" and not st.session_state.vectorstore:
                st.warning("No active document set to add to. Please 'Create New Document Set' first or load an existing one.")
                st.stop() # Stop execution

            uploaded_pdf_names = [pdf.name for pdf in pdf_docs]
            
            if process_option == "Create New Document Set":
                doc_set_id_to_process = generate_document_set_id(uploaded_pdf_names)
                
                # Check if this exact set of files already exists
                if doc_set_id_to_process in st.session_state.doc_sets_metadata:
                    st.info("A document set with these exact files already exists. Loading it instead of reprocessing.")
                    st.session_state.current_doc_set_id = doc_set_id_to_process
                    # Load existing vectorstore
                    with st.spinner("Loading existing vector store..."):
                        try:
                            embeddings = get_embeddings_model()
                            if not embeddings: st.stop()
                            loaded_vectorstore = FAISS.load_local(
                                get_faiss_index_path(doc_set_id_to_process),
                                embeddings,
                                allow_dangerous_deserialization=True
                            )
                            st.session_state.vectorstore = loaded_vectorstore
                            st.session_state.chat_history = load_chat_history(doc_set_id_to_process)
                            st.session_state.conversation = get_conversation_chain(loaded_vectorstore, st.session_state.chat_history)
                            st.success(f"Loaded existing document set: {st.session_state.doc_sets_metadata[doc_set_id_to_process]['name']}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error loading existing vector store: {e}")
                            st.session_state.vectorstore = None
                            st.session_state.conversation = None
                            st.session_state.chat_history = [] # Clear history on error
                            st.session_state.current_doc_set_id = "default_documents" # Fallback
                            st.stop()
                
                with st.spinner("Processing new documents and creating new set..."):
                    documents = get_pdf_documents_with_metadata(pdf_docs)
                    if documents is None: st.stop()

                    st.text("Splitting text into chunks...")
                    text_chunks = get_text_chunks(documents)

                    vectorstore = get_vectorstore(text_chunks)
                    if vectorstore is None: st.stop()

                    # Save new FAISS index
                    faiss_save_path = get_faiss_index_path(doc_set_id_to_process)
                    os.makedirs(faiss_save_path, exist_ok=True)
                    try:
                        vectorstore.save_local(faiss_save_path)
                        st.success("Vector store processed and saved!")
                    except Exception as e:
                        st.error(f"Error saving vector store: {e}")
                        st.stop()
                    
                    # Update metadata and session state
                    final_set_name = new_doc_set_name if new_doc_set_name else f"Documents_{doc_set_id_to_process[:6]}"
                    st.session_state.doc_sets_metadata[doc_set_id_to_process] = {
                        "name": final_set_name,
                        "files": uploaded_pdf_names,
                        "faiss_path": faiss_save_path,
                        "chat_history_path": get_chat_history_file_path(doc_set_id_to_process)
                    }
                    save_document_set_metadata(st.session_state.doc_sets_metadata)
                    st.session_state.current_doc_set_id = doc_set_id_to_process
                    st.session_state.vectorstore = vectorstore
                    st.session_state.chat_history = [] # New set, new history
                    save_chat_history([], doc_set_id_to_process)
                    st.session_state.conversation = get_conversation_chain(vectorstore, []) # Re-initiate chain with empty history
                    st.success(f"'{final_set_name}' created and loaded!")
                    st.rerun() # Refresh UI
                    
            elif process_option == "Add to Current Document Set":
                current_doc_set_id = st.session_state.current_doc_set_id
                current_doc_set_name = st.session_state.doc_sets_metadata[current_doc_set_id]['name']

                with st.spinner(f"Adding documents to '{current_doc_set_name}'..."):
                    documents = get_pdf_documents_with_metadata(pdf_docs)
                    if documents is None: st.stop()

                    st.text("Splitting text into chunks...")
                    text_chunks = get_text_chunks(documents)

                    # Add to existing vector store
                    updated_vectorstore = get_vectorstore(text_chunks, st.session_state.vectorstore)
                    if updated_vectorstore is None: st.stop()

                    # Save updated FAISS index
                    faiss_save_path = get_faiss_index_path(current_doc_set_id)
                    try:
                        updated_vectorstore.save_local(faiss_save_path)
                        st.success("Documents added and vector store updated!")
                    except Exception as e:
                        st.error(f"Error saving updated vector store: {e}")
                        st.stop()
                    
                    # Update metadata with new files
                    existing_files = st.session_state.doc_sets_metadata[current_doc_set_id]["files"]
                    new_unique_files = list(set(existing_files + uploaded_pdf_names)) # Add unique new files
                    st.session_state.doc_sets_metadata[current_doc_set_id]["files"] = new_unique_files
                    save_document_set_metadata(st.session_state.doc_sets_metadata)
                    
                    st.session_state.vectorstore = updated_vectorstore
                    st.session_state.conversation = get_conversation_chain(updated_vectorstore, st.session_state.chat_history)
                    st.success(f"Documents successfully added to '{current_doc_set_name}'!")
                    st.rerun() # Refresh UI

        st.markdown("---")

        # --- Load Existing Document Sets ---
        st.markdown("#### Load Saved Document Sets")
        
        available_doc_sets = {
            metadata["name"]: doc_id
            for doc_id, metadata in st.session_state.doc_sets_metadata.items()
            if os.path.exists(get_faiss_index_path(doc_id)) and os.listdir(get_faiss_index_path(doc_id)) # Check if directory exists and is not empty
        }

        if available_doc_sets:
            current_selected_index = 0
            if st.session_state.current_doc_set_id in st.session_state.doc_sets_metadata:
                current_active_set_name = st.session_state.doc_sets_metadata[st.session_state.current_doc_set_id]["name"]
                if current_active_set_name in available_doc_sets:
                    current_selected_index = list(available_doc_sets.keys()).index(current_active_set_name)

            selected_doc_set_name = st.selectbox(
                "Select a saved document set:",
                options=list(available_doc_sets.keys()),
                index=current_selected_index,
                key="select_doc_set"
            )
            
            selected_doc_set_id = available_doc_sets[selected_doc_set_name]

            if st.button("Load Selected Set", key="load_set_button"):
                if st.session_state.current_doc_set_id == selected_doc_set_id:
                    st.info(f"'{selected_doc_set_name}' is already the active document set.")
                    st.stop()

                with st.spinner(f"Loading '{selected_doc_set_name}'..."):
                    try:
                        embeddings = get_embeddings_model()
                        if not embeddings: st.stop()
                        loaded_vectorstore = FAISS.load_local(
                            get_faiss_index_path(selected_doc_set_id),
                            embeddings,
                            allow_dangerous_deserialization=True
                        )
                        st.session_state.vectorstore = loaded_vectorstore
                        st.session_state.current_doc_set_id = selected_doc_set_id
                        st.session_state.chat_history = load_chat_history(selected_doc_set_id)
                        st.session_state.conversation = get_conversation_chain(loaded_vectorstore, st.session_state.chat_history)
                        st.success(f"'{selected_doc_set_name}' loaded successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading saved vector store for '{selected_doc_set_name}': {e}")
                        st.session_state.vectorstore = None
                        st.session_state.conversation = None
                        st.session_state.current_doc_set_id = "default_documents" # Fallback
                        st.session_state.chat_history = load_chat_history("default_documents") # Load default history if fallback
                        st.stop()

        else:
            st.info("No saved document sets found.")

        st.markdown("---")
        st.markdown("#### Delete Document Set")
        
        delete_doc_sets_options = {
            metadata["name"]: doc_id
            for doc_id, metadata in st.session_state.doc_sets_metadata.items()
            if os.path.exists(get_document_set_path(doc_id))
        }
        
        if delete_doc_sets_options:
            selected_delete_set_name = st.selectbox(
                "Select set to delete:",
                options=list(delete_doc_sets_options.keys()),
                key="select_delete_set"
            )
            
            delete_id = delete_doc_sets_options[selected_delete_set_name]

            confirm_delete = st.checkbox(f"Are you sure you want to delete '{selected_delete_set_name}' and all its data (including history)?", key="confirm_delete_checkbox")

            if st.button("Delete Selected Set", key="delete_set_button", disabled=not confirm_delete):
                if delete_id == st.session_state.current_doc_set_id:
                    st.warning("Cannot delete the currently active document set. Please switch to another set (or process new documents to create a new active set) before deleting this one.")
                    st.stop()
                else:
                    with st.spinner(f"Deleting '{selected_delete_set_name}'..."):
                        try:
                            import shutil
                            shutil.rmtree(get_document_set_path(delete_id))
                            del st.session_state.doc_sets_metadata[delete_id]
                            save_document_set_metadata(st.session_state.doc_sets_metadata)
                            st.success(f"'{selected_delete_set_name}' deleted successfully!")
                            st.rerun() # Refresh UI to remove deleted set from options
                        except Exception as e:
                            st.error(f"Error deleting set: {e}")
                            st.stop()
        else:
            st.info("No document sets to delete.")

if __name__ == '__main__':
    main()