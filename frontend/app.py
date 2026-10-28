"""Streamlit client for the FastAPI-backed Gemini content studio."""
import streamlit as st

from frontend.ui_helpers import (
    FEATURES,
    LENGTHS,
    TONES,
    FrontendAPIError,
    api_request,
)

st.set_page_config(
    page_title="AI Content Studio | Gemini",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container { max-width: 1180px; padding-top: 2.4rem; }
.hero { border:1px solid rgba(110,120,130,.23); border-radius:18px;
        padding:26px 30px; background:linear-gradient(110deg,rgba(72,113,246,.09),rgba(7,168,143,.055)); }
.hero h1 { margin:0; letter-spacing:-.8px; }
.hero p { opacity:.78; font-size:1.02rem; margin:9px 0 0; }
.tag {display:inline-block;border-radius:40px;padding:5px 13px;
      background:rgba(70,112,237,.11);margin-bottom:11px;font-size:.8rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="tag">PROJECT 01 · GENERATIVE AI + LLM</div>
  <h1>✨ AI Content Studio</h1>
  <p>Write, rewrite, summarize, and explore ideas with Google Gemini.</p>
</div>
""", unsafe_allow_html=True)
st.write("")

with st.sidebar:
    st.subheader("🛠️ Your writing workspace")
    st.caption("Gemini LLM • Python • FastAPI • Streamlit")
    st.markdown("**Generation settings**")
    tone = st.selectbox("Tone", TONES, index=0)
    length = st.select_slider("Response length", options=LENGTHS, value="medium")
    temperature = st.slider(
        "Creativity (temperature)", min_value=0.0, max_value=1.0,
        value=0.6, step=0.1, help="Lower is more focused; higher allows more variation."
    )
    language = st.selectbox("Output language", ["English", "Telugu", "Hindi", "Spanish", "French"])
    st.divider()
    st.caption("AI-generated output may contain mistakes. Review before sharing.")
    st.caption("This application uses a direct LLM API, without RAG or autonomous agents.")

tab_create, tab_chat, tab_about = st.tabs(["🪄 Content tools", "💬 AI chat", "ℹ️ About this project"])

with tab_create:
    left, right = st.columns([1.03, 1], gap="large")
    with left:
        st.markdown("### Create something useful")
        selected = st.selectbox("Choose a tool", list(FEATURES.keys()))
        task, label, example = FEATURES[selected]
        with st.form("generate_form"):
            user_input = st.text_area(
                label, placeholder=example, height=220, max_chars=12000,
                help="Describe the task clearly or paste the text to transform."
            )
            generate_clicked = st.form_submit_button(
                "✨ Generate content", type="primary", use_container_width=True
            )
        if generate_clicked:
            if not user_input.strip():
                st.warning("Add some text or a topic before generating.")
            elif len(user_input.strip()) < 3:
                st.warning("Please enter at least three characters.")
            else:
                with st.spinner("Gemini is drafting your content..."):
                    try:
                        answer = api_request("/generate", {
                            "task": task,
                            "input_text": user_input,
                            "tone": tone,
                            "length": length,
                            "language": language,
                            "temperature": temperature,
                        })
                    except FrontendAPIError as exc:
                        st.error(str(exc))
                    else:
                        st.session_state.generated_result = answer["generated_text"]
                        st.session_state.generated_model = answer.get("model", "Gemini")
                        st.session_state.generated_tool = selected
                        st.success("Content generated!")

    with right:
        st.markdown("### Your result")
        if "generated_result" in st.session_state:
            st.caption(
                f"{st.session_state.get('generated_tool', 'Generation')} "
                f"• {st.session_state.get('generated_model', 'Gemini')}"
            )
            st.text_area(
                "Edit or copy the result", value=st.session_state.generated_result,
                height=350, key=f"output_{hash(st.session_state.generated_result)}"
            )
            st.download_button(
                "⬇️ Download as .txt",
                data=st.session_state.generated_result,
                file_name="ai_content_studio_output.txt",
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.info("Select a tool, enter your text, and click **Generate content** to see the output here.")
            st.markdown("**Includes:** email writing · LinkedIn posts · summaries · rewriting · blogs")

with tab_chat:
    st.markdown("### Chat with Gemini")
    st.caption("Chat history stays in this browser session; only the last 12 messages are sent as context.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Ask a question or brainstorm an idea...")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = api_request("/chat", {
                        "message": prompt,
                        "history": st.session_state.chat_history[-12:],
                        "temperature": temperature,
                    })
                except FrontendAPIError as exc:
                    st.error(str(exc))
                else:
                    st.markdown(result["reply"])
                    st.session_state.chat_history.extend([
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": result["reply"]},
                    ])
    if st.button("🧹 Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

with tab_about:
    st.markdown("""
    ### What you're learning in this project
    - **Generative AI:** generating new text from instructions.
    - **Large Language Models:** Google Gemini processes each prompt.
    - **Prompt Engineering:** separate system instructions, task context, and user input.
    - **Backend APIs:** FastAPI validates and forwards requests without exposing the Gemini key to the browser.
    - **Full-stack Python:** Streamlit frontend communicates with FastAPI via HTTP.

    **Not included (on purpose):** retrieval/vector databases, document RAG,
    function-calling agents, or multi-agent workflows. Those are separate projects.

    **Privacy:** Your input is sent to the configured FastAPI server and then to
    the Google Gemini API for processing. Avoid submitting sensitive personal information.
    This demo does not save content to a database.
    """)
