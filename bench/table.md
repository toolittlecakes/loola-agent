| task | arm | run | success | turns | tool calls (bash) | compactions | prompt | cached | completion | s | error |
|---|---|---|---|---|---|---|---|---|---|---|---|
| changelog | before | 1 | ✅ | 5 | 8 (0) | 0 | 174763 | 103680 | 2670 | 42 |  |
| changelog | before | 2 | ❌ | 5 | 12 (0) | 0 | 191496 | 109952 | 2168 | 38 | ❌ The next request may need ~95070 tokens, more than the 96000-token window allows (compaction is disabled). |
| changelog | after | 1 | ✅ | 14 | 21 (0) | 0 | 217234 | 174464 | 7149 | 57 |  |
| changelog | after | 2 | ✅ | 13 | 25 (0) | 1 | 194354 | 135040 | 8771 | 78 |  |
| hot-files | before | 1 | ❌ | 19 | 26 (0) | 0 | 1035560 | 922368 | 11641 | 171 | ❌ The next request may need ~89287 tokens, more than the 96000-token window allows (compaction is disabled). |
| hot-files | before | 2 | ❌ | 8 | 15 (0) | 0 | 318296 | 228864 | 4038 | 55 | ❌ The next request may need ~88758 tokens, more than the 96000-token window allows (compaction is disabled). |
| hot-files | after | 1 | ✅ | 18 | 53 (0) | 1 | 546309 | 406912 | 16842 | 134 |  |
| hot-files | after | 2 | ✅ | 23 | 59 (0) | 1 | 772231 | 627328 | 22863 | 186 |  |
