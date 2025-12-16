import streamlit as st
from streamlit_agraph import Node, Edge, Config, agraph
from master_verifier import run_pipeline, answer_question
from report_generator import generate_report
from config import *

st.set_page_config("Offline Research Verifier", layout="wide")
st.title("🔍 Offline Research Verification System")

files = st.file_uploader(
    "Upload research PDFs",
    type=["pdf"],
    accept_multiple_files=True,
    key="pdf_uploader"
)

tabs = st.tabs(["Verification", "Chatbot", "Reports"])

if files:
    pages, chunks, claims, verification = run_pipeline(files)

    # -------- Verification --------
    with tabs[0]:
        for idx, r in enumerate(verification):
            st.markdown("---")
            st.markdown(f"### Claim\n{r['claim']}")

            nodes = [Node("claim", "Claim", 35, "#EF4444")]
            edges = []

            for j, m in enumerate(r["matches"]):
                nid = f"m_{idx}_{j}"
                nodes.append(
                    Node(
                        nid,
                        f"{m['pdf']} | p{m['page']} | {m['score']}",
                        25,
                        "#22C55E"
                    )
                )
                edges.append(Edge("claim", nid))

            agraph(
                nodes=nodes,
                edges=edges,
                config=Config(
                    height=GRAPH_HEIGHT,
                    width=GRAPH_WIDTH,
                    directed=True,
                    physics=True
                ),
                key=f"verification_graph_{idx}"
            )

    # -------- Chatbot --------
    with tabs[1]:
        question = st.text_input("Ask a question from the PDFs", key="chat_input")
        if st.button("Ask", key="chat_button"):
            answer, sources = answer_question(question, chunks)
            if not answer:
                st.error("Answer not found in provided documents.")
            else:
                st.success("Answer")
                st.write(answer)

    # -------- Reports --------
    with tabs[2]:
        if st.button("Generate Verification Report", key="report_btn"):
            path = generate_report(verification)
            with open(path, "rb") as f:
                st.download_button(
                    "Download Report",
                    f,
                    file_name=path,
                    key="download_report"
                )
