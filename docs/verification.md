# 验证记录

快照日期：2026-09-13。测试环境：macOS，Codex CLI 0.153.4，Node.js 20.20.0，Bun 1.3.5。

- 三个插件均通过当前 plugin-creator 的 manifest / skills 校验。
- 在临时 CODEX_HOME 中实际注册 marketplace、安装三个插件、查询 installed/enabled 状态、移除插件和 marketplace。没有复制当前用户认证文件。
- 安装后的全部分发文件与源目录逐文件一致：45 个 P-Stack skills、28 个飞书 skills、4 个阅读 skills。
- 从安装后的 P-Stack 执行可选 agent setup，写入临时项目和临时 user-home；两个模板成功展开，重复安装内容一致。真实用户 agent 配置未改动。
- 新增 ONV 验收 skill 完整文件校验与 CLI 检查；doctor 在依赖完整的临时笔记上通过，在笔记位于给定 vault 之外时正确拒绝。
- 阅读验证器：纯 Markdown 测试笔记通过；不存在的附件被正确拒绝。PDF 渲染链路不在本次迁移验证范围。
- P-Stack orchestrator / watch-pr：54 个 Bun 测试通过，TypeScript strict typecheck 通过。
- P-Stack model policy / Benny state machine：17 个 Node 测试通过。
- Obsidian skill 通过 skill-creator 校验；已移除私人 vault 路径和主笔记名称。
- 对分发文件检查常见凭据格式和旧电脑路径，未发现凭据或私人路径。飞书材料中的示例 ID 和 P-Stack 测试中的 `/Users/operator` 是原分发中的示例，不是当前用户资料。

发布后已从公开 GitHub 仓库再次运行完整隔离安装检查并通过；安装提示词的匿名 HTTP 访问返回 200，GitHub 仓库可见性为 public。

可重复执行：

```bash
python3 scripts/verify_install.py
# 发布后从 GitHub 重新安装验证：
python3 scripts/verify_install.py --source spotify2junkie/codex-skill-kit
```

没有验证公司电脑的网络、账号权限、可用模型，或新 Codex 任务中的运行时 skill 发现。飞书登录/业务 API 未调用。hooks 受信任状态、可选自动化、PDF 产出能力需目标环境按实际请求验证。

`plugins/pstack-for-codex/tests` 中其余测试和上游兼容性记录作为来源资料保留；本迁移版本并未宣称原上游整套 release suite 全部通过。根目录本记录与 `scripts/verify_install.py` 是迁移包的验证入口。

## 2026-09-21：可选 Skill 管理插件

新增独立 `skill-maintenance` 插件（1 个 `skill-maintainer`），默认迁移仍为原三个插件。验证环境为 Codex CLI 0.155.0-alpha.9.2。

- skill-creator `quick_validate.py` 与 plugin-creator `validate_plugin.py` 均通过。验证依赖 PyYAML 安装在临时 venv，未改全局 Python。
- `python3 scripts/verify_install.py` 通过：四个插件分别包含 45/28/4/1 个 skills，安装文件逐字节一致，原模板和阅读验证器回归通过。
- 新 Skill 与管理指南的相对链接均可解析；公开分发文件不含个人绝对路径。
- 独立 agent 使用新 Skill 在隔离夹具中执行一次真实合并：两个阅读 Skill 合并为 batch-note，默认一篇、显式逐篇，保留来源链接、不确定性、LaTeX、每篇限制说明和禁止外发规则；调用者已迁移，重复入口已移除。父任务检查了实际输出文件。
- How 对包结构做只读解释；Swarm 对实现和交付做独立复核。这是候选版本的案例验证，不是基线对照实验，也不是量化 Skill Lift。

未验证自动触发、真实阅读输出生成、多次随机运行或不同模型表现；这些不能由结构校验或上述一次维护任务替代。P-Stack 源码未改，本次不重新宣称其上游完整 release suite 通过。

## 2026-09-22：Reading Radar 完整工作流

`reading-notes` 从 4 个 skills 更新为 5 个，新增 `reading-radar`，并同步最新版 `obsidian-paper-note` 的架构/Loss 批判性精读、批量 manifest、来源审查和逐页视觉审查契约。Poteto Mode、Swarm、Recall 与 Teach 继续由 `pstack-for-codex` 提供，没有在阅读插件中复制同名入口。

- `python3 -m unittest discover -s plugins/reading-notes/skills/obsidian-paper-note/scripts -p 'test_verify_note_bundle.py'`：21 个回归测试通过。
- `python3 scripts/verify_install.py --source .`：四个插件分别包含 45/28/5/1 个 skills；隔离安装、逐文件一致性、Reading Radar 打包、笔记验证器和 ONV vault 边界检查全部通过。
- 插件版本更新为 `reading-notes 1.1.0+codex.20260922075602`。
- 保留可移植边界：没有加入私人 Obsidian 路径、旧笔记、凭据、聊天记录或运行时缓存。

当前结构验证不能证明未来模型一定正确触发 Skill，也不能替代真实 Top N 搜索、来源 Review、PDF 逐页查看或目标机器的运行时验证。
