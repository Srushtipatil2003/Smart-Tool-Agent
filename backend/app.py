# backend/app.py (FIXED INTEGRATED BACKEND CODE)
import os
import sys
import chromadb
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import Settings
from llama_index.core.agent.workflow import FunctionAgent

# Path correction patch for smooth execution across environments
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.tools import calculate_speed_fine, mock_toll_wallet_deduction

# =====================================================================
# PHASE 1: INITIALISE FASTAPI & CHROMADB
# =====================================================================
app = FastAPI(title="Smart Toll AI Agent System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "YPUR API KEY"
google_llm = GoogleGenAI(model="gemini-2.5-flash", api_key=API_KEY)
google_embed = GoogleGenAIEmbedding(model="models/text-embedding-004", api_key=API_KEY)

# Assign settings globally
Settings.llm = google_llm
Settings.embed_model = google_embed

# Ensure data directory and file exist before proceeding
os.makedirs("data", exist_ok=True)
law_file_path = os.path.join("data", "traffic_laws.txt")

# Read the file contents directly using native Python to ensure 100% ID isolation
if os.path.exists(law_file_path):
    with open(law_file_path, "r", encoding="utf-8") as f:
        law_text_content = f.read()
else:
    law_text_content = "No traffic law data available."

# Build a completely isolated, clean Chroma Client
print("[Backend] Creating in-memory index...")

clean_document = Document(
    text=law_text_content,
    doc_id="static_smart_city_law_book"
)

index = VectorStoreIndex.from_documents(
    [clean_document],
    embed_model=google_embed
)

query_engine = index.as_query_engine()

print("[Backend] In-memory index created successfully.")
print("[Backend] ChromaDB initialization complete.")


# =====================================================================
# PHASE 2: INITIALISE THE AI AGENT
# =====================================================================
def lookup_traffic_laws(violation_description: str) -> str:
    """
    Searches the official smart city traffic laws and penal code database.
    Use this to look up specific penalty sections, flat rates, and rules for a violation type.
    """
    return str(query_engine.query(violation_description))


agent = FunctionAgent(
    name="toll_inspector_agent",
    description="An intelligent traffic enforcement agent that evaluates vehicle logs, checks legal frameworks, and handles fine processing.",
    tools=[lookup_traffic_laws, calculate_speed_fine, mock_toll_wallet_deduction],
    llm=google_llm
)


# =====================================================================
# PHASE 3: FASTAPI WEB ENDPOINTS
# =====================================================================
@app.post("/process-toll/")
async def process_toll(vehicle_id: str, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        csv_data_string = df.to_string()

        execution_prompt = f"""
        You are acting as the automated smart toll scanner engine for Vehicle ID: '{vehicle_id}'.
        Below is the raw telemetry sensor log matrix extracted from the vehicle's onboard sensor recorder:
        CRITICAL SYSTEM OPERATION INSTRUCTION: 
        To avoid overloading network buffers, you MUST introduce a structural mental pause between evaluating each violation row. Do not execute tools concurrently. Take your time to think sequentially.

        {csv_data_string}

        Please perform these tasks systematically:
        1. Examine each recorded violation entry row by row.
        2. For flat-rate violations (e.g., Turning, Parking, Honking), run `lookup_traffic_laws` to extract the exact legal cost penalty string specified in the penal documentation.
        3. For variable 'Overspeeding' violations, execute `calculate_speed_fine` passing the exact 'Posted_Limit' and 'Actual_Speed' column numbers from the row to ensure zero-error computational math.
        4. Sum up all individual fine numbers to calculate the exact aggregate 'total_fine'.
        5. Pass that 'total_fine' value and the 'vehicle_id' string directly into the `mock_toll_wallet_deduction` function tool to execute the live financial toll gate checkout clearance event.

        Return your final answer strictly as a clean, easy-to-read textual report. State each violation found, the individual calculated fine itemized breakdown, the total cumulative fine amount, and copy the transaction output statement from the deduction tool word-for-word.
        """

        agent_response = await agent.run(execution_prompt)
        return {
            "status": "success",
            "vehicle_id": vehicle_id,
            "report": str(agent_response)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/")
def read_root():
    return {"status": "online", "message": "Smart City Toll Server API is operating normally."}
