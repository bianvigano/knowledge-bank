1|# Memory-context system v1 (June 24, 2026): Tutorial notes on vault-graph functionality — ended up in ~Documents/vault-graph (GH bianvigano/vault-graph). 7-module Graphify-style pipeline. Install: git clone + bash install.sh. CLI query: vq PATH query/explain/search/god/communities. Depends on Hermes + Trae integration for automatic detection. 

> MODULES
> 1. vault-graph.parse - fetches & parses API responses
> 2. vault-graph.compose - generates visual representations
> 3. vault-graph.merge - combines multiple sources into single graph

> INTEGRATION
> ~/.hermes/mcps/vault-graph/ config enables stdio IPC in Hermes
> Initial alias created auto CLI references ~/bin/vq
> Used with memory-context SQLite storage for persistent graph snippets

> KEY CONCEPTS
> - CLI query pattern: `vq path explain`<
> - Integration with Hermes workflow triggers
> - Data flows through memory-context SQLite
> - Self-contained executable avoids import issues

| Source | USER PROFILE X% — Y/Z chars | ACTION | RESULT PERCENT\nArchived |
|--------|---------------------------|--------|----------------------|
| vault-graph standalone repo | git clone + install.sh | Omitted CLI alias setup: must manually add ~/bin to PATH and verify vq alias works | 0 |