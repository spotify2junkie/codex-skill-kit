# Codex Skill Kit

把个人电脑上的工程、飞书和论文阅读能力迁移到另一台电脑的 Codex。仓库是可直接安装的 Codex marketplace，保留 skills 需要的脚本、模板和参考资料。

| 插件 | 内容 | 默认安装 |
| --- | --- | --- |
| `pstack-for-codex` | 45 个 P-Stack skills；保留本机 Poteto Mode 的调整 | 是 |
| `lark-work` | 28 个飞书 skills：文档、知识库、多维表格、表格、消息、日历、会议、任务等 | 是 |
| `reading-notes` | Reading Radar Top N 搜索/Review、Obsidian 论文精读、ELI5 图解与笔记/PDF 验收，共 5 个 skills | 是；存储配置稍后确定 |
| `skill-maintenance` | 1 个原创 Skill：冲突审计、更新、合并与行为验证 | 按需安装 |

## 发给新电脑 Codex

复制 [INSTALL_PROMPT.md](INSTALL_PROMPT.md) 的整段文字，或直接说：

> 请读取 https://github.com/spotify2junkie/codex-skill-kit 的 README.md 和 BOOTSTRAP.md，在这台电脑的 Codex 中安装 P-Stack、飞书和完整阅读插件，保留现有配置。阅读 skills 一并安装，笔记内容和存储位置等我确定后再迁移；检查依赖与安装结果，飞书首次使用时再配置公司身份。

## 安装

需要支持 `codex plugin` 的 Codex CLI。已在 `codex-cli 0.153.4` 上完成隔离安装验证。先执行 `codex plugin --help`；命令不存在时使用公司允许的更新或安装方式，勿猜测配置格式。

```bash
codex plugin marketplace add spotify2junkie/codex-skill-kit --ref main
codex plugin add pstack-for-codex@personal
codex plugin add lark-work@personal
codex plugin add reading-notes@personal
codex plugin list --json
```

marketplace 名称是 `personal`，与 GitHub 仓库名不同。若已存在同名 marketplace，先按 [BOOTSTRAP.md](BOOTSTRAP.md) 检查来源，保留原有配置。

安装后新建一个任务，让 Codex 重新加载 skills。插件安装成功不代表飞书账号已授权，也不代表当前旧任务的 skill 索引已刷新。

## 使用

- 工程：`$poteto-mode 帮我修复这个问题，完成相关验证。`
- 理解代码：`$how 解释这个请求如何经过各层。`
- 飞书：`查看我今天的日程`、`读取这篇飞书文档并总结`，可按描述自动选择对应 skill。
- 阅读包启用后：`$reading-radar 搜索这个 topic 的 Top 20，名单确认后合并制作 Obsidian 精读。`

Poteto Mode 保留本机的自动发现设置；其他 P-Stack skills 保留各自原有调用策略。可选 agent profiles 不固定模型，安装插件也不会创建 Benny 自动化。

## 依赖与首次配置

- **P-Stack**：基础说明可直接使用；Node.js 20+ 支撑 `.mjs` 工具。Bun 支撑 orchestrator / watch-pr，相关工具按锁文件安装依赖。GitHub 操作需要新电脑自己的 `gh` 授权；旧电脑凭据不迁移。
- **飞书**：需要官方 `@larksuite/cli`。本快照对应旧电脑已安装的 `1.0.93`。新电脑优先沿用公司提供的 CLI；缺失时按 [BOOTSTRAP.md](BOOTSTRAP.md) 安装匹配版本。首次使用按照 `lark-shared` 完成配置和公司账号授权；新版本与快照不兼容时按官方说明同步更新。
- **阅读**：Markdown 分析不依赖旧 vault；验证器需要 Python 3.10+，完整 PDF 验收需要 Poppler 和 ImageMagick；PDF 创作与图解工作流还需要目标环境可用的 PDF skill 和浏览器。缺少时明确列出，不声称 PDF 流程已就绪。

## 阅读 skills 一起安装，笔记架构稍后迁移

```bash
codex plugin add reading-notes@personal
```

[完整阅读包](docs/reading-kit.md)迁移 Topic → 候选池 → 独立 Review → Top N 冻结 → 精读制作与验收的完整方法，包含图解风格、笔记与 PDF 验收脚本及全部配套说明。没有旧笔记、附件、私人 vault 路径、iCloud 配置或笔记应用设置。确定使用 Obsidian、飞书或其他载体后，再配置目标位置和附件策略。迁移到其他载体时需要适配写入与嵌入语法；不把 Obsidian 的 `![[...]]` 当作跨平台格式。

## 更新与移除

先查看变更；更新后重新安装需要更新的插件，并新建任务：

```bash
codex plugin marketplace upgrade personal
codex plugin remove lark-work@personal
codex plugin add lark-work@personal
```

同样适用于另两个插件。只移除需要更新或删除的插件；保留用户配置、凭据以及 `$setup-pstack` / `$setup-benny` 创建的文件。它们由对应 skill 的 receipt 流程管理。

## 来源与验证

[来源记录](sources.json)、[P-Stack 本机改动清单](docs/local-pstack-changes.json)、[验证记录](docs/verification.md)。P-Stack 和飞书保留各自 MIT 许可与声明。个人阅读 skills 是当前快照，未额外授予开源许可。

仓库不包含 Codex/飞书/GitHub 凭据、聊天记录、公司数据、旧笔记或 `node_modules`。安装只注册本仓库插件，不替换全局 `AGENTS.md`，不固定模型，不创建自动化。

## Skill 管理、冲突与合并

新增可选插件 `skill-maintenance`，不改变 P-Stack 上游快照。使用方法、公开参考材料和验证记录见 [管理指南](docs/skill-maintenance.md)。

```bash
# 尚未注册本仓库时，按上面的安装步骤注册；已注册且来源匹配时更新索引：
codex plugin marketplace upgrade personal
codex plugin add skill-maintenance@personal
```

新建任务后使用：

> $skill-maintainer 检查我指定的这些 skills，区分重复、触发重叠和规则冲突。保留现有能力与权限边界，完成必要的更新、合并及验证，告诉我改了什么和如何回退。

[直接阅读 SKILL.md](plugins/skill-maintenance/skills/skill-maintainer/SKILL.md)；[公开研究材料](plugins/skill-maintenance/skills/skill-maintainer/references/sources.md)。无需私人 Obsidian 路径。
