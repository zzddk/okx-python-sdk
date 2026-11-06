# 导入包改名 okxsdk

0.16.0 之后这个仓库成为独立发行：发行名 `okx-python-sdk`，但 import 包仍叫 `okx`，与上游 `python-okx` 冲突——同一环境安装两个包时，后装的会覆盖先装的 `okx/`，两个 SDK 的模块混在一起。

我们决定：**import 包名改为 `okxsdk`，目录 `okx/` 改为 `okxsdk/`，所有 `from okx...` 改为 `from okxsdk...`；发行名保持 `okx-python-sdk`。** 这是破坏性变更，进 0.17.0，并在 CHANGELOG 的 Migration 表逐行列出。

## Considered Options

- **保留 `okx`，只改发行名**：PyPI 上两个发行名不同，但 import 仍冲突，属于最坏的一种「装上了但互相覆盖」。
- **发行名也继续叫 `python-okx`**：PyPI 上已被上游占用，无法发布；仓库名也可能与上游混淆。
- **把包名改成 `okx_python_sdk`**：更长，且与发行名不完全对应；`okxsdk` 更短、与 `okx-python-sdk` 对应。

## Consequences

- 所有用户代码的 import 需要改：`from okx import Account` → `from okxsdk import Account`；`pip install python-okx` → `pip install okx-python-sdk`。
- 包内相对导入、`py.typed`、`package_data`、测试与示例同步改；历史 ADR 与 `.scratch` 工单里的 `okx/` 路径保留为当时的记录，不回写。
- 与上游共存：两个包可以同时安装，import 名不同。
