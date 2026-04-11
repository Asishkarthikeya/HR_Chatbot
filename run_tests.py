import os
import sys
import logging

# Setup barebones logging for test script
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.graph import get_graph

def run_test_scenario():
    print("=" * 60)
    print("TESTING ICE QAgent E2E Workflow")
    print("=" * 60)
    
    app = get_graph()
    
    # ── Scenario 1: Initial query (QA) ──
    query1 = "What is the difference between UI and API testing in QA?"
    print(f"\n[Scenario 1] Initial Query:\n>> '{query1}'")
    
    inputs = {
        "query": query1,
        "chat_history": []
    }
    
    # Stream the graph response
    print("\nRunning graph...")
    final_state = None
    for output in app.stream(inputs):
        for key, value in output.items():
            print(f"Node output: {key}")
            final_state = value
            
    print(f"\n[Response 1 from {final_state.get('agent')}]:")
    print("-" * 40)
    print(final_state.get('response'))
    print("-" * 40)
    print(f"Confidence: {final_state.get('confidence')}")
    
    # Append to chat history
    chat_history = [
        {"role": "user", "content": query1},
        {"role": "assistant", "content": final_state.get('response')}
    ]
    
    # ── Scenario 2: Ambiguous Follow-Up Query ──
    query2 = "What about for performance testing?"
    print(f"\n[Scenario 2] Follow-Up Query (Conversation-Aware):\n>> '{query2}'")
    
    inputs2 = {
        "query": query2,
        "chat_history": chat_history
    }
    
    print("\nRunning graph with chat history...")
    final_state2 = None
    for output in app.stream(inputs2):
        for key, value in output.items():
            print(f"Node output: {key}")
            final_state2 = value
            
    print(f"\n[Response 2 from {final_state2.get('agent')}]:")
    print("-" * 40)
    print(final_state2.get('response'))
    print("-" * 40)
    print(f"Confidence: {final_state2.get('confidence')}")
    
    print("\n" + "=" * 60)
    print("E2E Test Complete!")

if __name__ == "__main__":
    run_test_scenario()
