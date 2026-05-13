"""
Buffett Agent Gradio UI.
Provides a simple chat interface for internal testing.
"""

# --- SQLite Fix for CodeSandbox / Low-version SQLite ---
# This must be imported before chromadb
import sys
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass
# -------------------------------------------------------

from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
from engine.skill_executor import SkillExecutor

# Automatically get the current directory to support local and CodeSandbox environments
# This fixes the "Role directory 'buffett' not found" error
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    executor = SkillExecutor(ROOT_DIR)
except Exception as e:
    print(f"Warning: Could not initialize SkillExecutor: {e}")

def chat_with_buffett(message: str, history: list):
    """Handle chat messages using the SkillExecutor."""
    if not message.strip():
        return history
    
    if history is None:
        history = []

    # 1. Add user message (Gradio v5+ format: dictionary with role and content)
    history.append({"role": "user", "content": message})

    try:
        # 2. Call LLM/RAG
        response = executor.run("buffett", message)
        # Remove mock prefix if present
        display = response.replace("[模拟 LLM 回复]: ", "")
    except Exception as e:
        display = f"系统处理出错: {str(e)}"
    
    # 3. Add assistant message
    history.append({"role": "assistant", "content": display})
    
    return history

def clear_history():
    return []

with gr.Blocks(title="巴菲特投资顾问") as app:
    gr.Markdown("# 🏦 巴菲特投资顾问 AI")
    gr.Markdown("基于 Skill + RAG + Memory 架构。可提问投资理念、公司分析、市场观点等。")
    
    # Removed bubble_full_width for compatibility with newer Gradio versions
    chatbot = gr.Chatbot(
        height=500,
        avatar_images=("👤", "👨‍💼")
    )
    
    with gr.Row():
        msg_input = gr.Textbox(
            placeholder="输入您的问题... (例如: 什么是保险浮存金?)",
            scale=4,
            show_label=False
        )
        send_btn = gr.Button("发送", scale=1, variant="primary")
    
    clear_btn = gr.Button("清空对话", size="sm")
    
    msg_input.submit(chat_with_buffett, [msg_input, chatbot], chatbot)
    send_btn.click(chat_with_buffett, [msg_input, chatbot], chatbot)
    clear_btn.click(clear_history, outputs=chatbot)

if __name__ == "__main__":
    # Theme parameter moved to launch() in newer Gradio versions
    app.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
