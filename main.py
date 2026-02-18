from agent import LumenAgent

def cli():
    agent_instance = LumenAgent()
    print("\n" + "="*50)
    print("LUMEN: DISTRIBUTED AGENTIC MIDDLEWARE")
    print("="*50)
    print("Available IDs: 101, 102")
    
    while True:
        uid = input("\n User ID (or 'exit'): ")
        if uid.lower() == 'exit': break
        
        req = input("Request (e.g. 'name' or 'full profile'): ")
        
        inputs = {
            "user_id": uid, "user_request": req,
            "data_pool": {}, "next_step": "", "final_output": "", "visited": []
        }
        
        print("\n--- Execution Flow ---")
        result = agent_instance.graph.invoke(inputs)
        
        print("\n--- Final Response ---")
        print(result['final_output'])
        print("-" * 50)

if __name__ == "__main__":
    cli()