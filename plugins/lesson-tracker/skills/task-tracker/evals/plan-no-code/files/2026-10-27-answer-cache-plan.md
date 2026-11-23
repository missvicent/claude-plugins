# Answer cache for the RAG assistant

**Goal:** Cache answers to repeated questions so the assistant skips retrieval and generation when the same question comes back within a day, while never serving an answer from a document version that has since changed.

## Steps

1. **Cache key.** Normalize the question (lowercase, strip punctuation) and hash it together with the tenant id.
2. **Store.** An in-memory dict with a 24-hour TTL per entry; no external cache yet.
3. **Invalidation.** Drop every entry whose cited chunk ids include a chunk that was re-ingested with a new version.
4. **Metrics.** Count hits and misses per tenant and log the hit rate once an hour.

## Open questions

- Should near-identical questions ("refund time?" vs "how long do refunds take?") share an entry, or only exact matches after normalization?
- Does the cache need a size limit before we move to an external store?
