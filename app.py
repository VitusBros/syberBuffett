"""
Buffett Agent Gradio UI.
Provides a simple chat interface for internal testing.
"""
import gradio as gr
from engine.skill_executor import SkillExecutor

executor = SkillExecutor("/workspace")

def chat_with_buffett(message: str, history: list):
    """Handle chat messages using the SkillExecutor."""
    if not message.strip():
        return "请输入您的问题。"
    
    response = executor.run("buffett", message)
    # Remove mock prefix for display
    display = response.replace("[模拟 LLM 回复]: ", "")
    return display

def clear_history():
    return []

with gr.Blocks(title="巴菲特投资顾问") as app:
    gr.Markdown("# 🏦 巴菲特投资顾问 AI")
    gr.Markdown("基于 Skill + RAG + Memory 架构。可提问投资理念、公司分析、市场观点等。")
    
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
    app.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
