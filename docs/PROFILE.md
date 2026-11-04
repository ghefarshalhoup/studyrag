# Profile copy

Use the repository link after the prepared changes are published: **https://github.com/ghefarshalhoup/studyrag**. The text below describes the implemented project, not a deployed production service.

## GitHub repository description

LangGraph document assistant with reproducible retrieval evaluation: BM25, dense, hybrid and reranking, frozen questions, source-traceable judgments and offline replay.

## GitHub topics

`python`, `langgraph`, `langchain`, `rag`, `information-retrieval`, `evaluation`, `bm25`, `semantic-search`, `hybrid-search`, `reranking`, `streamlit`

Pin this repository on the GitHub profile. Keep the README, final findings and case study as the three main entry points.

## CV project entry

**StudyRAG — RAG assistant and retrieval evaluation** | Python, LangGraph, Streamlit

- Built a document assistant with page/source metadata, relevance filtering, conversation memory and tested abstention when all evidence is rejected.
- Implemented reproducible evaluation of BM25, dense, hybrid and reranked retrieval using frozen questions, AI-reviewed pooled relevance judgments, nDCG/MRR, latency measurements and offline ranking replay.

Short version if space is tight:

Built a LangGraph document assistant and reproducible retrieval evaluation; compared four approaches using nDCG/MRR, explicit relevance judgments and latency, exposing a reranker's development-to-final-check tradeoff.

## LinkedIn Featured item

**Title:** StudyRAG | LangGraph RAG and retrieval evaluation

**Description:** A document assistant plus a reproducible comparison of keyword, dense, hybrid and reranked retrieval. Includes source-traceable evidence, frozen development/final questions, regression tests and model-free replay. The final check showed why a development gain alone did not justify a reranker's added CPU latency.

## Short application message

One project that reflects how I work is StudyRAG. I built a LangGraph document assistant and extended it with a reproducible retrieval evaluation. I compared BM25, dense search, hybrid search and reranking using frozen questions, explicit relevance judgments and latency measurements. Reranking looked better during development, but nearly tied BM25 on the reserved questions while adding around 3.4 seconds per query. The repository includes the evidence, failure cases and commands to replay the results without paid APIs.

## Interview points to understand before using this project

- Explain why rejected evidence must not be restored as a fallback, and why state must be committed before a completion event.
- Explain why RRF combines ranks instead of mixing incompatible BM25/cosine scores.
- Distinguish nDCG, ordinary MRR, direct-evidence MRR and pooled recall.
- Explain why the dataset is a prospective same-corpus holdout, and why its AI judgments are not independent human gold.
- Describe one reranker improvement and one regression from the final findings.

Avoid describing this project as production-deployed, human-gold evaluation, a Qdrant-backed application or an MCP integration. Those claims are not supported by this repository. The live app uses an in-memory vector store; the additional retrievers are evaluated separately.
