# Badminton review report — IMG_8678.MOV

- Source: `/Users/yh/ops/tmp/badminton-cut/IMG_8678.MOV`
- Source duration: 467.127s
- Rendered duration: 49.003s (10.49% of source)
- Clips: 4
- Category coverage: core_technique, highlight_point, improvable_rally
- Video: `/Users/yh/src/codex-skill-kit-wt-a/artifacts/skillkit2/a/IMG_8678/deliverables/review.mp4`
- Output: 2560×1440 h264 bt709/bt709/bt709, 78.3 MB
- Local render validation: PASS
- Visual subtitle inspection: PASS (five source/output frame pairs; lower-third center, readable, sampled racket/shuttle contacts remain visible)
- Remote QA bot: not run

## Segment margins and findings

## rally-01 — core_technique (做得好)

- Clip: `00:00:34.000`–`00:00:46.500`
- Serve contact: `00:00:37.000`; pre-serve margin: **3.000s**
- Dead ball: `00:00:45.000`; post-dead-ball margin: **1.483s**
- Reason: 近侧搭档在后场起拍，粉色上衣球员守在前场并参与连续回合，能看到双打前后站位与衔接。
- Improvement drill: 双打前后轮转：后场高远球、前场封网，出现平抽时并步回中，完成 6 轮后交换前后位置。
- Expert findings:
  - 技术动作 at `00:00:39.000`: 粉色上衣球员前场击球使用短促挥拍，拍头留在身体前方。
  - 步法站位 at `00:00:40.000`: 前场球员重心降低并保持面向球网，搭档留在后场覆盖。
  - 战术球路 at `00:00:42.000`: 近侧组合前后分工明确，前场封挡后仍保留后场接续位置。

## rally-02 — improvable_rally (做得不好)

- Clip: `00:01:13.000`–`00:01:26.000`
- Serve contact: `00:01:15.200`; pre-serve margin: **2.195s**
- Dead ball: `00:01:24.000`; post-dead-ball margin: **1.992s**
- Reason: 白色上衣搭档多次向前场扑救，来球连续压在前场后身体回收较慢，左右覆盖容易拉开。
- Improvement drill: 双打前场两点移动：搭档在后场维持直线球，前场球员左右各做弓步拦截并回到中前场，6 组。
- Expert findings:
  - 技术动作 at `00:01:20.000`: 低位救球时上身较前倾，触球后需要用非持拍手帮助平衡。
  - 步法站位 at `00:01:21.000`: 白色上衣搭档跨步到前场后仍朝向侧线，回到中路的第一步偏慢。
  - 战术球路 at `00:01:23.000`: 连续回放低球使搭档反复留在网前；可挑向后场中路争取回位时间。

## rally-03 — highlight_point (做得好)

- Clip: `00:04:26.000`–`00:04:37.000`
- Serve contact: `00:04:28.200`; pre-serve margin: **2.198s**
- Dead ball: `00:04:35.000`; post-dead-ball margin: **1.985s**
- Reason: 粉色上衣球员完成前场压迫，搭档从后场及时跟进，回合以对手落地球结束。
- Improvement drill: 发接后第三拍：前场截击后搭档跟进封网，若对手挑高球则回到前后进攻位，8 球一组。
- Expert findings:
  - 技术动作 at `00:04:30.000`: 前场球员在身体前方用短挥拍控制来球，击球后拍头迅速回到准备位置。
  - 步法站位 at `00:04:32.000`: 前场球员压上后，后场搭档向中前场补进，形成前后接续。
  - 战术球路 at `00:04:34.000`: 继续把球压在对手前场并由搭档跟进，迫使对手以低点回应。

## rally-04 — core_technique (做得好)

- Clip: `00:05:57.500`–`00:06:10.000`
- Serve contact: `00:05:59.700`; pre-serve margin: **2.198s**
- Dead ball: `00:06:08.000`; post-dead-ball margin: **1.987s**
- Reason: 粉色上衣球员在网前用短促动作连续处理来球，搭档保持后场覆盖，回合结束前的轮转完整可见。
- Improvement drill: 网前封挡加后场补位：前场连续两次短球控制，后场搭档跟进中路，失去进攻时同步回防，6 轮。
- Expert findings:
  - 技术动作 at `00:06:03.000`: 网前触球采用短挥拍，拍头快速回到身前，有利于接下一拍。
  - 步法站位 at `00:06:04.000`: 前场与后场搭档保持纵向站位，前场球员触球后没有完全离开网前。
  - 战术球路 at `00:06:06.000`: 继续在前场控制线路，让后场搭档保持接续准备；注意失去进攻后同步回到防守位。

## Visual and timestamp spot checks

- Manual source/output timestamp checks: **5/5 match** (minimum required: 4/5).
- Subtitle placement: lower-third center and readable in the inspected frames; sampled racket/shuttle contacts remain visible.

| Output time | Source time | Clip | Result |
|---:|---:|---|---|
| 4.500s | 38.500s | rally-01 | Match |
| 15.000s | 75.500s | rally-02 | Match |
| 27.000s | 267.500s | rally-03 | Match |
| 40.000s | 361.000s | rally-04 | Match |
| 47.000s | 368.000s | rally-04 | Match |

## Reference comparison

对同一源视频 IMG_8678.MOV 做了候选流程的完整时段浏览，并复核入选回合附近的密集帧；同时审阅 BadmintonCoachSkill 本地快照。差异如下：

- 输出类型：BadmintonCoachSkill 是证据型教学诊断 skill，没有与本候选相同的整回合剪辑器；本候选输出成片、回合时间表和复盘报告。
- 诊断字段：参考规范要求问题、可见证据、证据边界、原因、纠正原则、练习和复测指标；本候选包含做得好/不好、原因、练习及技术/步法/战术三类带时间点结论，但没有单列复测指标。
- 回合编辑：本候选记录发球前/死球后的实测留白、三类回合覆盖、编码和成片时长；参考项目没有对应的成片编辑门槛。
- 对比范围：本轮未运行参考项目运行时，因此这里比较同一源视频上的工作流和报告契约，不是两份运行时输出或成片的实测对比。

## QA status

This report records local automated media checks. It does not represent a remote QA bot result.
