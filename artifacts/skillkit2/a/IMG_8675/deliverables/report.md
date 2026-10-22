# Badminton review report — IMG_8675.MOV

- Source: `/Users/yh/ops/tmp/badminton-cut/IMG_8675.MOV`
- Source duration: 487.073s
- Rendered duration: 52.006s (10.68% of source)
- Clips: 4
- Category coverage: core_technique, highlight_point, improvable_rally
- Video: `/Users/yh/src/codex-skill-kit-wt-a/artifacts/skillkit2/a/IMG_8675/deliverables/fix1/review.mp4`
- Output: 2560×1440 h264 bt709/bt709/bt709, 83.1 MB
- Local render validation: PASS
- Visual subtitle inspection: PASS (four frames checked)
- Source boundary frame review: PASS (8 windows per clip, 8 fps)
- Boundary evidence manifest: `/Users/yh/ops/logs/skillkit2/a/fix1/evidence/final-reviewed/manifest.json`
- Expert finding to clip mapping: PASS
- Remote QA bot: not run

## Segment margins and findings

## rally-01 — core_technique (做得好)

- Clip: `00:01:10.000`–`00:01:19.300`
- Serve contact: `00:01:13.700`; pre-serve margin: **3.685s**
- Dead ball: `00:01:17.600`; post-dead-ball margin: **1.687s**
- Reason: 近侧球员完成发球后的接续击球，随后迅速回到准备状态，能看到发接球后的动作衔接。
- Improvement drill: 发球后连续第三拍练习：低发球、接发、回到双打防守位，重复 8 球并检查回位是否在对手触球前完成。
- Expert findings:
  - 技术动作 at `00:01:15.000`: 接发动作较紧凑，拍头在身体前方，减少了大幅后摆。
  - 步法站位 at `00:01:16.000`: 接发后能回到中前场准备区域；脚下仍可增加一次轻分腿垫步。
  - 战术球路 at `00:01:17.000`: 回球线路将对手留在网前，近侧搭档保持后场覆盖。

## rally-02 — improvable_rally (做得不好)

- Clip: `00:01:46.500`–`00:01:59.200`
- Serve contact: `00:01:49.600`; pre-serve margin: **3.085s**
- Dead ball: `00:01:57.600`; post-dead-ball margin: **1.588s**
- Reason: 粉色上衣球员前场接球时身体前倾明显，完成低位处理后没有立刻恢复到平衡准备位。
- Improvement drill: 两人网前挑放随机练习：每球触拍后先回到网前基准位，再出发接下一球，左右各 8 球。
- Expert findings:
  - 技术动作 at `00:01:55.000`: 低位触球时拍面在身前，但上身随手臂前探；练习降低重心而不折腰。
  - 步法站位 at `00:01:56.500`: 前场弓步后回位步骤不明显，双脚仍偏向来球一侧。
  - 战术球路 at `00:01:57.200`: 回合中使用较低的网前球，若对手已在网前，可改用挑球争取时间。

## rally-03 — highlight_point (做得好)

- Clip: `00:03:48.000`–`00:04:00.500`
- Serve contact: `00:03:51.600`; pre-serve margin: **3.595s**
- Dead ball: `00:03:58.000`; post-dead-ball margin: **2.495s**
- Reason: 近侧搭档在后场完成高点击球，粉色上衣球员留在前场支援，进攻回合随后结束。
- Improvement drill: 前后站位进攻练习：后场连续高点击球、前场封挡，出现回球过网时前场完成截击，6 组后交换位置。
- Expert findings:
  - 技术动作 at `00:03:56.000`: 后场球员在高点击球后有完整挥拍和随挥，击球点在头部上方。
  - 步法站位 at `00:03:54.500`: 前场球员保持在网前区域，后场搭档留出挥拍空间，没有明显交叉抢位。
  - 战术球路 at `00:03:57.500`: 持续向下压迫并由前场封住回球线路，进攻节奏连贯。

## rally-04 — improvable_rally (做得不好)

- Clip: `00:05:52.000`–`00:06:09.500`
- Serve contact: `00:05:55.600`; pre-serve margin: **3.588s**
- Dead ball: `00:06:07.000`; post-dead-ball margin: **2.487s**
- Reason: 回合末段粉色上衣球员仍站在前场偏右；可练习触球后并步回中，及时恢复准备位。
- Improvement drill: 前场触球后并步回中：交替喂直线与斜线球，击球后两步回到中线准备位，每侧 6 次。
- Expert findings:
  - 技术动作 at `00:06:06.500`: 回合末段粉色上衣球员仍保持站立；触球后可将拍头及时带回身前。
  - 步法站位 at `00:06:07.500`: 球死时粉色上衣球员仍站在前场偏右；可在击球后并步向中线回位。
  - 战术球路 at `00:06:05.500`: 回合末段粉色球员仍处于前场偏右；可挑向后场为回位争取时间。

## Reference comparison

对同一源视频 IMG_8675.MOV 做了候选流程的完整时段浏览，并复核入选回合附近的密集帧；同时审阅 BadmintonCoachSkill 本地快照。差异如下：

- 输出类型：BadmintonCoachSkill 是证据型教学诊断 skill，没有与本候选相同的整回合剪辑器；本候选输出成片、回合时间表和复盘报告。
- 诊断字段：参考规范要求问题、可见证据、证据边界、原因、纠正原则、练习和复测指标；本候选包含做得好/不好、原因、练习及技术/步法/战术三类带时间点结论，但没有单列复测指标。
- 回合编辑：本候选记录发球前/死球后的实测留白、三类回合覆盖、编码和成片时长；参考项目没有对应的成片编辑门槛。
- 对比范围：本轮未运行参考项目运行时，因此这里比较同一源视频上的工作流和报告契约，不是两份运行时输出或成片的实测对比。

## QA status

This report records local automated media checks. It does not represent a remote QA bot result.
