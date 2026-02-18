import os, requests
from typing import TypedDict, List
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq

load_dotenv()

class AgentState(TypedDict):
    user_id: str
    user_request: str
    data_pool: dict
    next_step: str
    final_output: str
    visited: List[str]

class LumenAgent:
    def __init__(self):
        # llama-3.1-8b-instant is perfect for this
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        self.graph = self._build_graph()

    def investigator(self, state: AgentState):
        """Reasoning Node: Checks for gaps and decides the next network call."""
        data = state['data_pool']
        req = state['user_request'].lower()
        
        # 1. Identify what the user wants
        is_full = any(x in req for x in ["full", "profile", "all", "email", "dept"])
        
        # 2. Check what we actually have
        has_name = "name" in data
        has_details = "email" in data
        
        # 3. Decision Logic
        if not has_name and "SERVICE_ID" not in state['visited']:
            decision = "SERVICE_ID"
        elif is_full and not has_details and "SERVICE_DIR" not in state['visited']:
            decision = "SERVICE_DIR"
        else:
            decision = "FINALIZE"

        print(f"   [Agent Decision]: {decision}")
        return {"next_step": decision}

    def fetcher(self, state: AgentState):
        """Action Node: Distributed Network Call."""
        step = state['next_step']
        uid = state['user_id']
        new_data = {}
        
        try:
            if step == "SERVICE_ID":
                print(f"   [Network] Calling Identity Service (8001)...")
                new_data = requests.get(f"http://localhost:8001/users/{uid}", timeout=5).json()
            elif step == "SERVICE_DIR":
                print(f"   [Network] Calling Directory Service (8002)...")
                new_data = requests.get(f"http://localhost:8002/directory/{uid}", timeout=5).json()
        except:
            new_data = {"error": "Connection failed"}

        return {
            "data_pool": {**state['data_pool'], **new_data},
            "visited": state['visited'] + [step]
        }

    def harmonizer(self, state: AgentState):
        """Output Node: Final JSON formatting."""
        prompt = f"""
        User Request: {state['user_request']}
        Data Collected: {state['data_pool']}
        
        Task: Provide a clean, structured JSON response. 
        If data is missing, just show what was found. 
        If the user was not found, return an error in the JSON.
        RETURN ONLY JSON. NO CHAT.
        """
        res = self.llm.invoke(prompt).content.strip()
        res = res.replace("```json", "").replace("```", "").strip()
        return {"final_output": res}

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("investigator", self.investigator)
        workflow.add_node("fetcher", self.fetcher)
        workflow.add_node("harmonizer", self.harmonizer)
        
        workflow.set_entry_point("investigator")
        workflow.add_conditional_edges("investigator", lambda x: x["next_step"], {
            "SERVICE_ID": "fetcher", 
            "SERVICE_DIR": "fetcher", 
            "FINALIZE": "harmonizer"
        })
        workflow.add_edge("fetcher", "investigator")
        workflow.add_edge("harmonizer", END)
        return workflow.compile()