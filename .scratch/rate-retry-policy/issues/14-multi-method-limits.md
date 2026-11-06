# 14 · 同路径多方法限额不同怎么处理

Type: grilling
Status: resolved
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

## Answer

同路径多方法的取数规则已定（2026-11-06，HITL grilling，`/grilling` + `/domain-modeling`）。**结论：规则 = 「按项目实际暴露的 HTTP 方法取值」，不取严、不取松；5 个值不同的路径里 4 个不在项目、1 个只有 POST，所以本图内不存在「单键该取谁」的实际歧义；14 无公开面变化。**

**事实核查（09 findings + 项目代码）**：

- 5 个值不同的路径与项目的关系：

| 路径 | POST | GET | 项目里有没有 |
|---|---|---|---|
| `/api/v5/account/bills-history-archive` | 12/day | 10/2s | **两侧都有**，但项目只暴露 POST（`okx/Account.py:279` 的 `BILLS_APPLY` 用 POST；`okx/consts/endpoints/account.py:54` 只此一个常量） |
| `/api/v5/account/mmp-config` | 2/10s | 5/2s | 仅官方有（项目无此路径常量） |
| `/api/v5/asset/monthly-statement` | 20/month | 10/2s | 仅官方有 |
| `/api/v5/rfq/mmp-config` | 1/10s | 5/2s | 仅官方有 |
| `/api/v5/users/subaccount/apikey` | 1/s | 20/2s | 仅官方有 |

- `/api/v5/trade/order-algo`：项目同时暴露 POST（`okx/Trade.py:115`）与 GET（`:191`），数值相同（均 20/2s），仅计数维度不同。
- `/api/v5/trade/order`：项目同时暴露 POST 与 GET（`PLACE_ORDER` / `ORDER_INFO`），数值相同（60/2s）、维度相同。
- 因此「取较严 / 取较松」在本项目的 274 个路径里**没有实际适用场景**：没有任何一条项目路径是「同时暴露两方法、官方值不同」。

1. **取数规则**：**按项目实际暴露的 HTTP 方法取值**，不取严、不取松。理由：取严会把 POST 的额度硬套到 GET（例如把 `bills-history-archive` 的 12/day 套到 GET 的 10/2s 上）；取松会让 POST 超限；按实际方法取值既不超限、也不过度限制，且可复现。
2. **5 个路径的具体处置**：① 4 个「仅官方有」的路径不进表——它们不在项目路径常量里，按 03 本就属「未收录端点」，**不是豁免、也不违反验收线**；② `bills-history-archive` 取 POST 的 `12 requests per day`（项目只调用 POST）；③ 主文档 12/day 与 Change Log 2026-06-11「改为 1/10s per user」冲突，按 02 取端点详情原文 12/day、按 10 的流程每次同步重新取证，14 不判定。
3. **`order-algo`**：记 `(20, 2)`（两方法数值相同，单键没有歧义）；「GET 维度 `User ID`、POST 维度 `(except Options): User ID + Instrument ID` / `(Options only): User ID + Instrument Family`」写进 spec 的「已知差异」清单，**不单独处理**（08 已定表不承载计数维度）。
4. **spec §② 的可复现规则**：写死「同路径多方法按项目实际暴露的 HTTP 方法取值；若将来出现项目同时暴露两方法、且官方值不同，该路径不进表并列入已知差异（`(method, path)` 升级属 Out of scope，届时另开 effort）；值相同只记数值，维度差异列入已知差异」；并附 `bills-history-archive` 的主文档/Change Log 冲突注记。
5. **公开面与 ADR**：以上都是**施工期的取数规则**，当前表仍是 8 条 → **14 无公开面变化、不建 0018、不写 `### Migration` 行**；07 留给本工单的「若决定改动则按三判据重判」触发条件**未触发**。

## 边界

- **08 的 Known limitation ② 注记（不改 08 正文）**：08 写「`/api/v5/trade/order` 同路径 POST + GET 共用一个配额」；09 查明两方法数值相同（60/2s、维度相同），所以它对 trade/order **不再是有歧义的 limitation**。真正有歧义的子集（5 个值不同）已由本工单的规则收口：4 个不在项目、1 个只有 POST。08 的决策未被推翻，只是事实细化，故**不重开 08**。
- **03 的验收线未被违反**：4 个「仅官方有」是**不在项目里**，不是豁免；`bills-history-archive` 正常收录。03 不重开。
- **14 自身无公开面变化**：不建 ADR、不写 `### Migration` 行、不新增 CHANGELOG 段；与 07 的判据一致。
- **不收图**：14 resolved 后 open 只剩 11（AFK research）与 12（`grilling`，被 11 阻塞）；frontier 只剩 11。14 是**最后一张无阻塞的 HITL 决策工单**，不代解、不收图、不触发子代理。
- 本图只决策，不改 `okx/consts/rate_limits.py` / `okx/consts/endpoints/`；不发版、不 push。

## Comments

- 2026-11-06: claimed → resolved（HITL grilling，两轮前沿收敛，用户确认共享理解；本会话未触发任何子代理、未新建工单）。
