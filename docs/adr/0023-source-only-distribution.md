# 只做源码分发，不再发布到 PyPI

0.17.0 从未上传到 PyPI（缺 API token；PyPI 上 `okx-python-sdk` 至今不存在）。ADR-0001 的发布策略建立在「已完成 PyPI 发布并被外部依赖」的前提上，ADR-0019 把发行名改成 `okx-python-sdk` 的动机之一也是「两个发行可在同一环境共存于 PyPI」。这两个前提都不再成立。

我们决定：**不再向 PyPI 发布任何版本。分发方式改为 GitHub 源码安装**（`pip install git+https://github.com/zzddk/okx-python-sdk.git`，或 clone 后 `pip install -e .`）。保留 `setup.py` / `MANIFEST.in` / `py.typed` / LICENSE 等打包元数据，因为源码安装本身就需要它们；CI 保留一次「能构建、能装」的冒烟验证，删掉 `twine`、`twine check` 与产物上传。

## Considered Options

- **继续发 PyPI**：需要 API token 或 Trusted Publishing，还要处理已公开但不可用的 `v0.17.0` tag；维护成本与收益不匹配。
- **连打包能力一起删**（去掉 setup.py 等）：会破坏 CI 的 `pip install -e .` 与本地开发，`py.typed` / LICENSE 也无法随包分发；源码安装本身就是一次构建，排除。
- **只停发布、保留打包元数据（采纳）**：分发路径变短，元数据正确性仍由 CI 冒烟验证兜住。

## Consequences

- ADR-0001 的「缺陷补丁先行」前提失效：没有 PyPI 升级路径，版本只体现在 git tag 与 CHANGELOG。仍按 minor/patch 语义打 tag（0.18.0 承接 `>=3.9` 这一破坏性改动，见 ADR-0004）。
- ADR-0019 的发行名 `okx-python-sdk` 保留（避免与上游 dist 名混淆），但「两个包可同时 pip install」不再适用；import 包 `okxsdk` 与上游 `okx` 不冲突这一点仍然成立。
- `pip install okx-python-sdk` 不可用；README、示例 notebook 与 CHANGELOG 的安装指引改为源码安装。
- `dev_requirements.txt` 去掉 `twine`；CI 的 BUILD JOB 改名「Packaging smoke test」，删 `twine check` 与 `actions/upload-artifact`。ADR-0021 Consequences 里提到的 `twine check` 验证由本决策取代，历史 ADR 不回写。
- 0.17.0 的坏 tag 保留在远端（删已推送的 tag 是破坏性共享操作，需单独确认），CHANGELOG 0.17.0 段标注废弃。
- 后续不再有 PyPI 上传、API token、Trusted Publishing 或 publish job 相关工作。
