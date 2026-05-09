import gradio as gr
from indexer import ChromaDBIndexer
from retriever import TutorRetriever

retriever = TutorRetriever()

def responder(pregunta: str) -> tuple[str, str, str]:
    try:
        result = retriever.ask(pregunta)
        fuentes = ", ".join(result.sources) if result.sources else "—"
        return result.answer, fuentes, result.backend_used
    except ValueError as e:
        return f"⚠️ Query bloqueada: {e}", "—", "—"
    except Exception as e:
        return f"❌ Error: {e}", "—", "—"

def indexar(source_dir: str) -> str:
    try:
        indexer = ChromaDBIndexer()
        ok = indexer.index_documents(source_dir or "./sources")
        return "✅ Documentos indexados correctamente" if ok else "⚠️ No se encontraron documentos"
    except Exception as e:
        return f"❌ Error: {e}"

with gr.Blocks(title="Tutor IA") as demo:
    gr.Markdown("# 🎓 Tutor Inteligente de IA\n**Stack híbrido: Ollama local + Groq nube**")

    with gr.Tab("💬 Consultar"):
        pregunta = gr.Textbox(
            label="Tu pregunta",
            placeholder="¿Qué es el algoritmo A*?",
            lines=2
        )
        btn_ask = gr.Button("Preguntar", variant="primary")
        respuesta = gr.Textbox(label="Respuesta", lines=6)
        fuentes_out = gr.Textbox(label="Fuentes citadas")
        backend_out = gr.Textbox(label="Backend usado")
        btn_ask.click(
            responder,
            inputs=pregunta,
            outputs=[respuesta, fuentes_out, backend_out]
        )

    with gr.Tab("📚 Indexar documentos"):
        dir_input = gr.Textbox(
            label="Ruta de documentos",
            value="./sources"
        )
        btn_idx = gr.Button("Indexar", variant="secondary")
        idx_status = gr.Textbox(label="Estado")
        btn_idx.click(indexar, inputs=dir_input, outputs=idx_status)

demo.launch(server_port=7860, share=False)
