# 完整阅读 Skill Kit

阅读包包含以下四个 skills 的完整目录；脚本、agents 元数据、features 和 references 均随插件安装。

| Skill | 作用 | 配套资源 |
| --- | --- | --- |
| `obsidian-paper-note` | 来源忠实的论文精读、主笔记追加、风险与迁移分析 | 笔记结构、证据边界、10 页 PDF 规范、存储约定、`verify_note_bundle.py` |
| `eli5` | 面向读者基础解释机制与代价 | 受众与类比约束 |
| `explain-eli5` | 卡通手绘、两格漫画式 HTML 图解 | 浅/深主题、术语与图示、浏览器渲染验证约定 |
| `verify-obsidian-notes` | Obsidian 笔记、嵌入 PDF 和框架图的验收 | `onv.py`、verification contract、四类 feature recipes |

## 工作流

`obsidian-paper-note` 组织内容，结合 `eli5` 与 `explain-eli5` 制作教学层；`verify_note_bundle.py` 检查笔记与附件。含 PDF 的严格精读使用 `verify-obsidian-notes` 的 doctor → verify → 查看每一页 → attest → status 流程。只有实际人工查看通过后才能得到最终视觉验收结论。

纯 Markdown 是用户明确选择的模式，此时只运行不要求 PDF 的 bundle 验证器。不能为了通过验证器制造 PDF 或视觉证明。

## 目标机器依赖

- Python 3.10+：两个验证脚本仅使用标准库。
- Poppler：`pdfinfo`、`pdftotext`、`pdftoppm`。
- ImageMagick：`magick`，生成联系表。
- 可用的 PDF 创作工具与 PDF skill：使用目标 Codex 自带/已安装的 PDF 能力；它属于运行环境，不复制旧电脑的整个运行时缓存。
- HTML 图解需要可用浏览器渲染能力；交付 PDF 时需实际查看所有渲染页。发布网页需目标环境的发布工具和相应授权，能力缺失时保留本地产物并报告。

这些系统工具不能由复制 skill 文件替代。按公司提供的安装方式补齐，再运行已安装 `verify-obsidian-notes/scripts/onv.py doctor --note <实际笔记> --vault-root <实际根目录>`。不要从旧电脑复制二进制、密钥或浏览器登录态。

## 安装与存储配置分开

默认一起安装四个阅读 skills。安装不会读取笔记、寻找旧 vault、创建新 vault，或修改 Obsidian 配置。

入职后确定载体，再把路径、主笔记命名、附件策略写进目标工作区的规则。继续用 Obsidian 时使用其 wikilinks；改为飞书等载体时保留内容与证据标准，并适配写入、附件和链接解析。ONV 当前验证的是 Obsidian 文件与 PDF，不宣称已支持其他平台。

## 本次查找范围

已检查全局 Codex / agents skills、Codex 项目和 worktrees 中的 SKILL.md、Claude/Cursor skills，以及已知 Obsidian vault 下的技能入口。新增发现的专用验收 skill 原先位于阅读任务工作区。重复备份不重复安装；P-Stack 中的通用写作与验证技能已随 P-Stack 包迁移。
