# Skill 管理、冲突、更新与合并

`skill-maintenance` 是独立可选插件，包含 `$skill-maintainer`。不修改 P-Stack 上游清单，不依赖私人笔记，也不要求安装 Swarm、Recall 或某种模型。

## 安装

先检查 `codex plugin marketplace list --json`，避免覆盖已有同名来源。首次注册本仓库：

```bash
codex plugin marketplace add spotify2junkie/codex-skill-kit --ref main
codex plugin add skill-maintenance@personal
```

若 `personal` 已指向本仓库，先 `codex plugin marketplace upgrade personal` 更新索引，再安装本插件。已安装本插件需要更新时，使用仓库 README 中的插件重装流程，仅重装 `skill-maintenance@personal`。新建任务后使用；不同时另装同名独立副本。

## 可直接复制的请求

审计，不改文件：

> $skill-maintainer 检查我提供的这些 skills，列出触发重叠、共享流程和规则冲突，引用具体规则，判断哪些应该合并、抽公共引用或保持独立。先只输出审计结果。

执行合并：

> $skill-maintainer 合并我指定的 A 和 B，保留全部已有能力、例外与权限边界；默认使用 A 的输出形式，显式请求时保留 B 的模式。同步调用者和相关资源，完成隔离验证，报告修改、未验证项和回退方式。

更新上游：

> $skill-maintainer 将指定技能更新到这个公开版本。比较旧上游、当前本地和新上游，保留本地定制，处理冲突，完成相关验证和已授权的安装。

给 AI 的材料：目标 skill 文件夹或仓库链接、要实现的行为、已知失败案例、需要保留的成功案例，以及目的地或发布范围。只给名称也可先定位，但无法找到实际文件时不能凭名称猜正文。参考论文只作背景；具体 skill 原文及实际行为才是合并依据。

## 设计依据

[入口 SKILL.md](../plugins/skill-maintenance/skills/skill-maintainer/SKILL.md) → [冲突决策](../plugins/skill-maintenance/skills/skill-maintainer/references/reconciliation.md) → [验证方法](../plugins/skill-maintenance/skills/skill-maintainer/references/verification.md)。

[公开材料与适用边界](../plugins/skill-maintenance/skills/skill-maintainer/references/sources.md)包括 OpenAI evals、ACES、SkillOpt 和 SkillChain。论文不是自动合并安全性的证明。本插件没有后台自更新或周期任务。

## 验证

包结构使用 skill-creator / plugin-creator 校验；可重复的真实隔离安装入口：

```bash
python3 scripts/verify_install.py
```

它验证四个分发插件、技能数量、安装后逐文件一致性以及现有模板和阅读验证器。具体版本的行为验证记录见 [verification.md](verification.md)。安装通过不等于自动触发或真实任务质量已获证明。
