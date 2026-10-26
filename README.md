# n8n portfolio workflows

Local n8n systems with no external credentials. The five workflows below were imported into n8n 2.32.7 on this Mac and executed successfully on 26 October 2026. The numbers in `runs/summary.json` and `portfolio-assets/` are from those runs. The records are sample data, not a client ledger.

| Workflow | What the local run did |
| --- | --- |
| `OrderCmdCenter01.json` | 36 orders. 4 quarantined, 4 rejected, 8 sent to review, 11 invoiced as parcels, 3 backordered, 6 held for pickup. Captured gross $4,714.20. Held gross $10,767.60. |
| `RevReconcile0001.json` | 26 invoices matched to cash, refunds, and chargebacks. 11 cleared, 5 still open, 4 sent to collections, 3 chargebacks, 3 overpaid. Leakage gap $6,790. |
| `SupportDesk00001.json` | 28 tickets. 6 escalated, 7 priority, 15 drafted auto-replies. 4 were already outside a 12-hour first response. |
| `ContentOpsFactory1.json` | 18 briefs. 4 compliance holds, 3 revisions, 8 longform packs, 3 social packs. |
| `IncidentCommand01.json` | 25 alerts collapsed into 8 incidents. 3 severity-1 bridges with a postmortem stub, 2 status drafts, 3 internal files. Estimated customer impact 580 minutes. |

Open a workflow with the manual trigger named "Run …". Each desk branch only runs when the sample data actually contains that case.

Cover images and result slides are in `portfolio-assets/`.

## Earlier drafts

These three need your own accounts (OpenAI, and where used HubSpot, Gmail, Google Sheets, Slack, Notion). They were imported on 18 September 2026 and have not been executed.

| File | What it does |
| --- | --- |
| `1-rag-knowledge-base-chatbot.json` | Upload a PDF, DOCX, or TXT, chunk it, embed it with OpenAI, store it in an in-memory vector store, and chat with an AI agent over that knowledge base. |
| `2-ai-lead-qualification-crm.json` | Take a form lead, enrich and score it, then route it through HubSpot, Gmail, Google Sheets, and Slack. |
| `3-ai-content-repurposing-factory.json` | Read a blog RSS feed and draft LinkedIn, X, and Instagram posts, with Notion, Google Sheets, and Slack. |

Import any file from **Workflows → Import from file** at `http://localhost:5678`. The five new workflows run from their manual trigger with the sample data already inside. The earlier drafts need your own credentials on the AI and SaaS nodes.
