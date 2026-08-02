import sys
import os
import traceback
import json
import re

# from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

print("Arguments:", sys.argv, file=sys.stderr)

# expected args: message, index_dir, optional mode ("chat" | "quiz")
if len(sys.argv) < 3:
    print("Usage: python langchain_query.py <message> <index_dir> [mode]", file=sys.stderr)
    sys.exit(1)

message = sys.argv[1]
index_dir = sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else "chat"
print(f"Mode: {mode}", file=sys.stderr)

# load prior turns (if present) so the LLM can keep context
history = ""
try:
    with open("history.txt", "r", encoding="utf-8") as f:
        history = f.read()
except FileNotFoundError:
    print("No history.txt found. Starting fresh.", file=sys.stderr)

# embeddings for retrieval
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

try:
    # open FAISS index
    print("Loading vector store from:", index_dir, file=sys.stderr)
    vectorstore = FAISS.load_local(index_dir, embedding_model, allow_dangerous_deserialization=True)

    # retrieve top-k relevant chunks for the user message
    print("Searching similar documents...", file=sys.stderr)
    docs = vectorstore.similarity_search(message, k=4)

    # join retrieved text into a single context blob
    print(" Querying with message:", message, file=sys.stderr)
    print(" Index loaded from:", index_dir, file=sys.stderr)
    print(" Top match snippet:", docs[0].page_content[:200] if docs else "No results found", file=sys.stderr)
    context = "\n\n".join(doc.page_content for doc in docs)
    print("Context length:", len(context), file=sys.stderr)

    # local LLM served by Ollama
    # llm = Ollama(model="llama3.2:3b", base_url="http://localhost:11434")
    llm = Ollama(model="llama3.1:70b", base_url="http://localhost:11434")
    # llm = Ollama(model="llama-3-8b", base_url="http://localhost:11434")
    # llm = Ollama(model="llama3.1:8b", base_url="http://localhost:11434")
    print("LLM loaded", file=sys.stderr)

    gesture_guide = """
Gesture meaning and usage guide:

acknowledging_pose:
Use when the avatar listens, acknowledges the student's input, or reacts with understanding.

thinking_pose:
Use when the avatar starts to think, analyzes a difficult question, or prepares an explanation.

head_nod_yes:
Use for agreement, confirmation, encouragement, greetings, or when saying that something is correct.

thoughtful_head_nod:
Use when the avatar agrees while still explaining or reflecting on the answer.

head_shake_no:
Use for corrections, negation, disagreement, or when explaining that something is not correct.

talk_pose:
Use as the default neutral speaking gesture during normal explanation.

talk_pose2:
Use as a second neutral speaking gesture to make longer explanations feel less repetitive.

talk_pose3:
Use as another neutral speaking gesture during calm explanation.

arm_gesture:
Use when emphasizing an important idea, transition, or explanation.

pointing_pose:
Use when highlighting an important concept, term, rule, or answer.

pointing_forward:
Use when directly addressing the student, for example with "you", "your answer", "look at this", or direct instruction.

surprised_pose:
Use only for unexpected, surprising, or emotionally emphasized moments.

hello_pose:
Use for greetings, introductions, or when welcoming the student.

bye_pose:
Use for farewells, goodbyes, or when ending the conversation.
"""

    # prompt: quiz mode expects Q/A style; chat mode answers based on retrieved context only
    if mode == "quiz":
        prompt_template = PromptTemplate(
            input_variables=["history", "context", "question", "gesture_guide"],
            template="""
You are a helpful tutor. Keep track of the ongoing conversation and be aware of whether you asked a question.

If the student chooses a topic or asks to continue with a topic, accept it and continue naturally.
Only grade the student if the previous assistant message clearly asked a factual quiz question.
Do not reject vague but understandable answers.
If not, continue the conversation helpfully or ask a new question.

Keep the tutor reply concise.
Use maximum 5 short sentences.
Do not create long lists.
Do not create bullet points.
Do not use bullet points or numbered lists.
Use normal spoken sentences only.

Use this format when asking:
Question: <question text>
Answer: <correct answer>

Also choose 3 to 5 body gestures for the avatar.

Use the following gesture guide:
{gesture_guide}

Gesture selection rules:
- Choose gestures that match the meaning and emotion of the tutor reply.
- Do not choose random gestures only for variety.
- Use mostly neutral speaking gestures for normal explanations.
- Use strong gestures such as surprised_pose, head_shake_no, or pointing_forward only when they clearly fit the sentence.
- The gestures should follow the order of the spoken reply.
- If no special gesture fits, use talk_pose, talk_pose2, or talk_pose3.

Return your answer exactly in this structure:

ANSWER:
<spoken tutor reply only>

GESTURES:
gesture1, gesture2, gesture3, gesture4, gesture5

Important:
- Your output must start with ANSWER:
- Do not write anything before ANSWER.
- Do not write gesture names inside the ANSWER section.
- Gesture names are only allowed after GESTURES.
- Do not repeat, copy, or summarize the conversation.
- Do not output "Conversation:" or "Student's latest message:".

Conversation:
{history}

Student's latest message:
{question}

Reply:
"""
        )
    else:
        prompt_template = PromptTemplate(
            input_variables=["history", "context", "question"],
            template="""
    You are a tutor. Use the context to ask ONE short quiz question OR grade the student's last answer.

    Rules:
    - Output must be SHORT (max 2-3 sentences).
    - Do NOT include "Current conversation", "Evaluation", or any meta commentary.
    - Do NOT repeat the full history.
    - If asking a quiz question, use EXACTLY this format:

    Question: <one question>
    Answer: <one short correct answer>

    If grading an answer, reply with:
    Correct. <1 short explanation>
    OR
    Not quite. <correct answer + 1 short explanation>

    Context:
    {context}

    History (for you only, do not repeat):
    {history}

    Student message:
    {question}

    Output:
    """
        )

    # run the chain with history + retrieved context + user message
    chain = LLMChain(llm=llm, prompt=prompt_template)
    print("Generating response...", file=sys.stderr)
    response = chain.run(history=history, context=context, question=message, gesture_guide=gesture_guide)

    # print only the final answer on stdout (server consumes this)
    raw = response.strip()

    allowed = {
        "acknowledging_pose", "thinking_pose", "head_nod_yes", "thoughtful_head_nod",
        "head_shake_no", "talk_pose", "talk_pose2", "talk_pose3", "arm_gesture",
        "pointing_pose", "pointing_forward", "surprised_pose", "hello_pose", "bye_pose"
    }

    answer = raw
    gestures = ["talk_pose", "talk_pose2", "arm_gesture"]

    # Split gestures if the model returned a GESTURES section.
    if "GESTURES:" in raw:
        answer_part, gesture_part = raw.split("GESTURES:", 1)
    else:
        answer_part = raw
        gesture_part = ""

    # If the model repeated the conversation before ANSWER, keep only the ANSWER part.
    answer_match = re.search(r"ANSWER\s*:?\s*(.*)", answer_part, re.DOTALL | re.IGNORECASE)
    if answer_match:
        answer = answer_match.group(1).strip()
    else:
        answer = answer_part.strip()

    parsed_gestures = [
        g.strip().replace("-", "_")
        for g in gesture_part.replace("\n", ",").split(",")
        if g.strip()
    ]

    parsed_gestures = [g for g in parsed_gestures if g in allowed]

    if parsed_gestures:
        gestures = parsed_gestures[:5]

    # append this turn to history.txt (best-effort)
    try:
        with open("history.txt", "a", encoding="utf-8") as f:
            f.write(f"\nStudent: {message}\nAI: {answer.strip()}\n")
    except Exception:
        print("Warning: could not update history.", file=sys.stderr)
        traceback.print_exc()

    while len(gestures) < 5:
        gestures.append("talk_pose")

    payload = {
        "response": answer,
        "gestures": gestures[:5]
    }

    print(json.dumps(payload, ensure_ascii=False), file=sys.stdout)

except Exception as e:
    # retrieval failed (e.g., missing index). Try direct LLM as a fallback.
    print("Vector load failed. Falling back to direct model response.", file=sys.stderr)
    traceback.print_exc()
    try:
        # llm = Ollama(model="llama3.2:3b")
        # llm = Ollama(model="llama3.1:8b")
        llm = Ollama(model="llama3.1:70b")
        # llm = Ollama(model="llama-tutor:latest")
        response = llm.invoke(message)
        print(response.strip())
    except Exception:
        # last-resort: bubble up failure
        print("Unable to respond at the moment.", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
