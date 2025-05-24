import streamlit as st
from langgraph_workflow import build_workflow
from chat_memory import memory

st.set_page_config(page_title="EspressoMind 🧠", layout="wide")
st.title("📚 Academic Research Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("Enter your research question:")

if st.button("Submit") and query:
    workflow = build_workflow()
    result = workflow.invoke({"input": query})
    st.session_state.chat_history.append((query, result["answer"]))
    st.write("### Answer:")
    st.write(result["answer"])

    st.write("### Chat History:")
    for q, a in st.session_state.chat_history:
        st.write(f"**Q:** {q}")
        st.write(f"**A:** {a}")
