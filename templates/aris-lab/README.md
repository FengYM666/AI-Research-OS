# ARIS 自动科研工作区模板

> 复制本目录（去掉 `-template` 后缀）到任意位置作为研究工作区。与 `aris-zhipu` 审稿桥 + ARIS 技能库 clone 配合使用。
> 详见仓库根 README 的「ARIS 深度科研流水线」一节。

## 三个文件各管什么

| 文件 | 谁维护 | 作用 |
|------|--------|------|
| `DIRECTIONS.md` | 你 | 研究方向池，一行一个方向，想跑就加一行 |
| `PROGRESS.md` | agent | 进度账本：每轮自动科研会话结束时更新（当前阶段/下一步/产出清单） |
| `README.md` | — | 本说明 |

## 使用方式（二选一）

**手动触发**：把方向写进 `DIRECTIONS.md`，对 agent 说「跑一轮 `<工作区路径>`」——它会读 `PROGRESS.md` 接着上次干。

**全自动（夜间无人值守）**：在 ZCode 里创建定时任务（CronCreate），prompt 参考 `../aris-nightly-cron-template.md`。
