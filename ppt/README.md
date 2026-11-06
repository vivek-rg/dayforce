# Five-slide presentation

Track 8 prepares `dayone_proof_final.pptx` and `dayone_proof_final.pdf`. Both should contain the same final five slides:

1. Problem and user value.
2. Product workflow and working demo.
3. Architecture and governed harness.
4. Safety, testing and measured evaluation results.
5. Future improvements and expected impact, labeled as hypotheses when unmeasured.

No fabricated benchmark, integration, customer or production-readiness claims. Cite the brief and relevant sources. Remove keys/private information from screenshots and speaker notes. Track 8 validates five slides, PDF legibility and consistency with the recorded commit. No presentation is included in the foundation.

PPTX and presentation PDFs are **not ignored**; after review use normal staging, for example `git add ppt/dayone_proof_final.pptx ppt/dayone_proof_final.pdf`. Publish only the actual final assets, not placeholders. For slide 3 explain the confirmed local SQLite prototype; slide 5 may mention managed PostgreSQL as a future shared-deployment option, **not a completed migration**. See [database decision and pitch wording](../docs/DATABASE_DECISION.md). Hosted model scope is Groq, Cerebras, Mistral, Gemini and OpenRouter plus local Ollama; label unimplemented/untested paths honestly.
