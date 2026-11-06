# 14 · 同路径多方法限额不同怎么处理

Type: grilling
Status: open
Blocked by: 09

## Question

由 [限额表条目要不要容纳计数维度与任意窗口](08-limit-entry-shape.md) 预留的触发条件而来。08 定「保持二元组 + `path` 单键、表不承载多方法区分」，并写明「09 若查出同路径多方法限额不同 → 新开工单、不重开 08」。

[官方已公布限额的端点清单与 274/135 差异核对](09-official-limit-endpoint-list.md) 的 findings（`research/official-limit-endpoint-list` 分支，commit `805528e`）查明 S1 完整版有 **9 个路径同时挂 POST + GET 两个端点声明**：

- **5 个 POST 与 GET 限额数值不同**：`/api/v5/account/bills-history-archive`、`/api/v5/account/mmp-config`、`/api/v5/asset/monthly-statement`、`/api/v5/rfq/mmp-config`、`/api/v5/users/subaccount/apikey`。
- **4 个数值相同**：含 08 特指的 `/api/v5/trade/order`（POST / GET 均 `60 requests per 2 seconds`、计数维度也相同，S1/S2/S3/S4 四份官方页面一致）。
- 另有 `/api/v5/trade/order-algo` **数值相同但计数维度不同**（GET 为 `User ID`，POST 为 `User ID + Instrument ID` / `User ID + Instrument Family`）。

在表保持 `path` 单键（08 已定，`(method, path)` 升级已写进地图 Out of scope）的前提下拍板：

1. 这 5 个数值不同的路径，`RATE_LIMITS` 里该记**哪个方法**的值？取较严 / 取较松 / 取 POST / 按项目实际调用方向挑——判据是什么？
2. 还是干脆**不收录**这 5 个路径、显式标为「未收录端点」维持不限流？03 的验收线（「官方已公布限额且与项目路径常量对应的端点」）是否允许这样豁免？
3. `/api/v5/trade/order-algo`（数值相同、维度不同）算不算需要处理？08 已定表不承载计数维度，这条是否只写进 spec 的「已知差异」清单即可？
4. 无论哪种选择，spec 的判定规则（07 骨架第 ② 节）要不要写一条「同路径多方法怎么取数」的可复现规则，供施工方补全表时遵守？
5. 每一处是否构成公开面变化、要不要进 ADR（0018 起）与 CHANGELOG 的 `### Migration`——由 [文档、CHANGELOG 与 ADR 怎么落](07-docs-and-adr.md) 统一判断归属。

解本工单时先 zoom 08 的 Answer 与 09 的 findings。只决策，不改 `okx/consts/rate_limits.py`。
