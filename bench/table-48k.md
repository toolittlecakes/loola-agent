| task | arm | run | success | turns | tool calls (bash) | compactions | prompt | cached | completion | s | error |
|---|---|---|---|---|---|---|---|---|---|---|---|
| changelog | before | 1 | ❌ | 1 | 2 (0) | 0 | 29892 | 0 | 308 | 17 | ❌ The next request may need ~74452 tokens, more than the 48000-token window allows (compaction is disabled). |
| changelog | before | 2 | ❌ | 1 | 1 (0) | 0 | 29892 | 0 | 184 | 15 | ❌ The next request may need ~52338 tokens, more than the 48000-token window allows (compaction is disabled). |
| changelog | after | 1 | ❌ | 5 | 9 (0) | 0 | 53243 | 39296 | 3968 | 55 | ❌ Compaction failed: the summary does not shrink the context enough (~69814 -> ~61497 tokens), and the context does not fit the 48000-token window. |
| changelog | after | 2 | ❌ | 5 | 11 (0) | 0 | 54026 | 39168 | 2989 | 49 | ❌ Compaction failed: the summary does not shrink the context enough (~68390 -> ~58964 tokens), and the context does not fit the 48000-token window. |
| hot-files | before | 1 | ❌ | 2 | 4 (0) | 0 | 60264 | 29824 | 669 | 21 | ❌ The next request may need ~40980 tokens, more than the 48000-token window allows (compaction is disabled). |
| hot-files | before | 2 | ❌ | 2 | 3 (0) | 0 | 60106 | 29824 | 393 | 18 | ❌ The next request may need ~52300 tokens, more than the 48000-token window allows (compaction is disabled). |
| hot-files | after | 1 | ❌ | 5 | 12 (0) | 0 | 78777 | 58240 | 4484 | 59 | ❌ Compaction failed: the summary does not shrink the context enough (~61744 -> ~47527 tokens), and the context does not fit the 48000-token window. |
| hot-files | after | 2 | ❌ | 5 | 13 (0) | 0 | 74582 | 55040 | 4782 | 68 | ❌ Compaction failed: the summary does not shrink the context enough (~61145 -> ~48457 tokens), and the context does not fit the 48000-token window. |
