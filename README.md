# n8n portfolio workflows

Three importable n8n workflows for a local n8n instance. Each file is a workflow export. Credentials stay in your own n8n account. These files do not contain API keys.

## Workflows

| File | What it does |
| --- | --- |
| `1-rag-knowledge-base-chatbot.json` | Upload a PDF, DOCX, or TXT, chunk it, embed it with OpenAI, store it in an in-memory vector store, and chat with an AI agent over that knowledge base. |
| `2-ai-lead-qualification-crm.json` | Take a form lead, enrich and score it, then route it through HubSpot, Gmail, Google Sheets, and Slack. |
| `3-ai-content-repurposing-factory.json` | Read a blog RSS feed and draft LinkedIn, X, and Instagram posts, with Notion, Google Sheets, and Slack. |

## Import into local n8n

1. Start n8n locally (`npx n8n`, default address `http://localhost:5678`).
2. Open **Workflows → Import from file** and choose one of the JSON files.
3. Open each workflow and attach your own credentials: OpenAI, and where used HubSpot, Gmail, Google Sheets, Slack, and Notion.
4. The in-memory vector store in the chatbot is for a local demo. Swap it for Pinecone, Qdrant, or Supabase if you need data to persist.

## Run status

These workflows were imported into a local n8n instance on this machine on 18 September 2026. They were left inactive and have not been executed.
