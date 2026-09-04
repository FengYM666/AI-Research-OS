# 执行纪律

## 执行前确认（Confirmation Gate）

- 复杂任务 / 3+ 文件改动 / 需求含糊 → 先出方案或先问（plan mode / AskUserQuestion），用户批准再动手
- 禁止猜方向盲干。方向不明确必须停下来问，不默认选一个方向闷头跑

## 计划拷问（Plan Grill）

写完计划、提交给用户之前，先自我拷问设计漏洞：

- 关键假设站得住吗？边界 / 空输入 / 异常路径覆盖了没？
- 计划跟用户真正要的一致吗？有没有理解偏差？
- 有没有过度工程、多余步骤、可砍的抽象？
- 失败场景是什么？出问题怎么退？

拷问发现的漏洞 → 修进计划再提交，别等用户发现。

### 触发条件（命中任一即拷问）

- 架构级决策：系统设计 / 数据模型 / API 设计
- 3+ 文件改动 / 跨模块 refactor
- 安全敏感：认证 / 支付 / 用户数据
- 高成本不可逆：数据迁移 / 部署 / 删库
- 用户明确要求（"grill me" / "审一下计划"）

### 不触发（跳过拷问）

- 1 文件小改 / typo / 快速查证 / 日常对话

## 代码改动后自动验证（强制）

每次写完 / 改完代码，说"完成"之前必须自动执行，不用等用户提醒：

1. 跑语法 / 类型检查或编译（cargo check / tsc / py_compile 等），别假设改动能编译
2. 用真实输入走一遍改动路径的逻辑；非平凡逻辑留一个能跑的 assert / 检查
3. grep 改动函数的所有调用方，修根因，不是只修用户报的那条路径
4. 查边界：空输入 / null / 边界值 / 溢出
5. 改了文件名、路径、符号名 → grep 所有旧名引用（文档内部交叉引用最容易漏）

# 找文件默认用 Everything

在用户电脑上找文件/软件/目录，默认用 Everything（NTFS 全盘索引，秒出结果），不要用 find 从根目录扫。安装位置可能被用户挪动，**禁止写死绝对路径**，每次现查再用：

1. 定位 es.exe（命令行搜索工具，和主程序 Everything.exe 同目录）：
   - 先试 `where es.exe`，在 PATH 里就直接用
   - 不在 PATH 就查注册表安装位置（软件挪走后重装它会自动更新）：
     ```bash
     dir=$(reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Everything" 2>/dev/null | grep -i InstallLocation | awk '{print $NF}'); dir=${dir//\\//}
     ```
     HKLM 没有就换 `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Everything`（用户级安装）
   - 注册表也没有才试常见位置：`D:\Everything`、`C:\Program Files\Everything`
2. 搜索：`"$dir/es.exe" -n 20 "关键词"`。常用参数：`-n` 限条数、`-path "目录"` 按路径过滤、`-extension ext` 按扩展名过滤
3. 报 "Everything IPC not found" → Everything 没在运行，用同目录主程序后台拉起：`"$dir/Everything.exe" -startup`，等几秒再重试
4. es 完全不可用的退路：GUI `"$dir/Everything.exe" -search "关键词"` + 截图读结果，或对已知小目录定向 ls/find

# Skill 中文注释

每次调用 Skill 工具后，回复末尾附一行 `— 中文说明`，讲这个 skill 是干什么用的。内置命令（/help、/clear 等）不用，非 skill 的正常对话不用。

# Global Memory

以下 memory 适用于所有项目。引用方式：`~/.zcode/memory/<文件名>`

- [Caveman 中文偏好](~/.zcode/memory/caveman-chinese-preference.md) — Caveman 模式用中文不是英文
- [三 Skill 协同](~/.zcode/memory/three-skill-synergy.md) — ECC + ponytail + PWF 三层工作流，省 token 保质量
- [Skill 中文注释](~/.zcode/memory/skill-chinese-annotation.md) — 每次 skill 调用自动跟中文说明
