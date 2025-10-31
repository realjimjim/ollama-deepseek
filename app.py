import ollama

messages = [{"role": "system", "content": "You are a knowledgeable AI."}]

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    messages.append({"role": "user", "content": user_input})

    print("AI: ", end="", flush=True)
    
    # Stream response in real-time
    stream = ollama.chat(
        model="phi3:mini",
        messages=messages,
        options={"temperature": 0.2, "top_k": 30, "top_p": 0.7},
        stream=True
    )
    
    reply = ""
    for chunk in stream:
        print(chunk['message']['content'], end="", flush=True)
        reply += chunk['message']['content']

    print()  # Move to next line after response
    messages.append({"role": "assistant", "content": reply})

