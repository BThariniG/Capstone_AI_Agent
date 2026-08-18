# Phase 4 — Add Knowledge & Retrieval (RAG)

## 1. Phase Overview

Phase 4 extends the Phase 3 AI Customer Support Resolution Agent by adding an authoritative knowledge source using **Retrieval-Augmented Generation (RAG)**.

Phase 3 demonstrated that integrating an LLM significantly improved semantic understanding, intent recognition, ambiguity handling, and safety behaviour compared with the Phase 2 rule-based baseline.

However, Phase 3 also identified an important limitation:

> The LLM could understand customer questions but did not have access to verified company-specific policies.

This resulted in hallucinations in early prompt variants and uncertainty in the final Prompt V3.

Phase 4 addresses this limitation by introducing:

- Company policy documents
- Text chunking
- Embeddings
- Semantic search
- A vector database
- Retrieval-Augmented Generation
- Missing-information handling
- Retrieval-quality evaluation

The selected **Prompt V3 from Phase 3** will remain the foundation of the agent because it demonstrated the strongest safety, privacy, uncertainty, and escalation behaviour.

---

# 2. Phase 3 → Phase 4 Motivation

## Phase 3 Finding

The LLM improved natural-language understanding but lacked authoritative business knowledge.

Example:

```text
Customer:
"What is your return policy?"

            ↓

Phase 3 V1
            ↓
Invented 30-day policy ❌


Customer:
"Can I return after 90 days?"

            ↓

Phase 3 V1
            ↓
Invented 90-day policy ❌


---

#Phase 4 - RAG - High Level Design

                PHASE 4 — RAG

              📚 COMPANY POLICIES
                     │
                     ▼
                 Read File
                     │
                     ▼
                Split Text
                     │
                     ▼
                Embeddings
                     │
                     ▼
                 Chroma DB
                     │
                     │
                     ├──────────────┐
                     │              │
                     ▼              │
👤 User Question → Semantic Search  │
                     │              │
                     ▼              │
              Relevant Chunks       │
                     │              │
                     └──────┬───────┘
                            ▼
                      Prompt V3 + Context
                            │
                            ▼
                         Mistral
                            │
                            ▼
                    Grounded Response

Langflow's official RAG guidance uses essentially this pattern: load a file, split the content into chunks, create embeddings, store them in a vector store such as Chroma, and query the vector store for relevant chunks before sending those chunks to the language model.