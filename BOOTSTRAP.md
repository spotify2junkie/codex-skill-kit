# 给执行安装的 Codex

用户发来的安装请求授权安装 P-Stack、飞书和完整阅读插件。按这台电脑现有公司规则执行；保留已有配置。仅笔记内容和存储配置延后。

## 1. 检查当前环境

运行 `codex --version`、`codex plugin --help`、`codex plugin marketplace list --json`、`codex plugin list --json`。查看 `node --version`、`bun --version`、`gh --version`、`lark-cli --version`，缺失项逐项记录。

`codex` 不在 PATH 时，使用当前 Codex app 已提供的 CLI 位置；不要套用旧电脑绝对路径，也不要因此要求用户提供旧电脑配置。命令不可用时采用公司允许的安装方式。

检查当前 Codex 的用户 skills 目录（尊重 CODEX_HOME），以及 `~/.agents/skills` 中是否已有同名 skills。若已有同一套插件或独立副本，先判断来源和差异；不要再装一份造成重复触发，也不要移除用户文件。

## 2. 注册和安装

本仓库 `.agents/plugins/marketplace.json` 的名称是 `personal`。

- 不存在此 marketplace：运行下面命令。
- 已存在且来源就是本仓库：复用；只有用户要求更新时才升级。
- 已存在但来源不同：不要覆盖。克隆本仓库到工作目录，通过目标环境可用的 plugin-creator 工具在新文件中生成唯一命名的 marketplace，再从这个本地目录安装。保留插件相对路径和原 marketplace。没有合适工具时说明名称冲突，取得具体选择后再处理。

```bash
codex plugin marketplace add spotify2junkie/codex-skill-kit --ref main
codex plugin add pstack-for-codex@personal
codex plugin add lark-work@personal
codex plugin add reading-notes@personal
codex plugin list --json
```

安装时会下载完整仓库，上述三个插件均启用。不能把三个包的 skills 混拷到一个目录：P-Stack 的 `setup-pstack` 和 `setup-benny` 依赖包根目录里的 templates / automations。

## 3. 工具与身份

基础 skill 安装和外部账号就绪分别报告。安装阶段不需要读取用户飞书消息或发送任何消息。

### P-Stack

Node.js 20+；Bun 仅在使用相关工具时必要。首次运行 Bun 工具会按 `skills/poteto-mode/scripts/bun.lock` 安装依赖，需网络。如果公司已有包管理约定，遵守其要求。

插件完整保留 hooks，但跨回合 sticky 模式需要 Codex 信任对应 hook 来源。没有受信任运行证据时只报告 current-turn-only。可选 agent profiles 由 `$setup-pstack` 后续按需配置，不在基础安装时创建。

### 飞书

优先使用公司提供的 lark-cli。若缺失且公司允许 npm 安装，可使用与快照对应的版本：

```bash
npm install -g @larksuite/cli@1.0.93
lark-cli --version
lark-cli --help
```

遇到已有新版本，先验证命令是否兼容，不降级公司已有工具。按 CLI `_notice` 和官方资料处理版本/skills 同步；此仓库固定快照不会自动追踪上游。

只有用户准备使用飞书时才读已安装 `lark-shared/SKILL.md`，按其 reference 指引运行 `config init` / `auth login`。确认公司身份、user/bot 与所需权限。授权 URL 配二维码；用户在官方页面操作，密钥不进入聊天、仓库或安装日志。首次登录需用户本人参与，不能用旧登录态替代。

### 完整阅读包

安装 `reading-notes` 内的全部 4 个 skills，详见 [reading-kit.md](docs/reading-kit.md)。检查 Python 3.10+、Poppler 的三个命令与 ImageMagick `magick`。PDF 创作和 HTML 图解还依赖目标环境的 PDF 与浏览器能力，缺项要报告。

安装阶段不寻找或创建 vault；用户确定目标存储载体后再配置。PDF skill/工具未就绪时，按用户选择提供 Markdown 分析或补齐依赖，不伪造 PDF 产物或验证结果。可以用临时测试笔记运行 ONV doctor 验证依赖，但这不是对真实笔记的验收。

## 4. 验证和交接

1. `codex plugin list --json` 中三个目标插件均已安装并启用。
2. 使用安装命令返回的 `installedPath` 检查 P-Stack 有 45 个 SKILL.md、飞书有 28 个、阅读有 4 个；确认 P-Stack templates、automations、hooks、脚本及 Bun 锁文件，以及阅读包的两个验证脚本、ONV features 和 verification contract 存在。
3. 可在独立临时项目和临时 user-home 中运行 `setup-pstack/scripts/manage-agents.mjs install --scope project ...`，证明模板路径正确；不写用户真实 agent profiles。
4. 汇报已安装插件、依赖缺项和账号待配置项。安装检查不等于运行时模型/权限/工具验证。
5. 请用户新建任务刷新 skill 索引。在新任务用 `$poteto-mode` 或 `$how` 做一个小型只读任务，确认实际发现。飞书实测等用户完成授权和给出真实查询后再做。
