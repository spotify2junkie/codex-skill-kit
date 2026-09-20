# 双图数据约定

一个 JSON 驱动两张图片、来源页及生成提示词。数值只能是真实核验的实验结果或 null；不能填“未知”字符串或用 0 冒充缺失。

```json
{
  "title": "本次鞋款选购指南",
  "date": "2026-09-20",
  "scope": "男款 US9 单只；室温主泡棉；吸震和回弹取后跟",
  "selection_note": "用户指定鞋单；按用途分组，非销量榜",
  "method_url": "https://runrepeat.com/testing-methodology",
  "notes": ["AC 不与 HA 换算；— 表示暂无同口径实测"],
  "groups": [{
    "id": "daily",
    "name": "日常使用",
    "basis": "用途假设与排序依据",
    "top3": [{
      "shoe_id": "shoe-a",
      "reason": "有来源的推荐理由",
      "tradeoff": "主要取舍",
      "evidence_urls": ["https://example.org/review"]
    }]
  }],
  "shoes": [{
    "id": "shoe-a",
    "brand": "Brand",
    "model": "Model A",
    "group_id": "daily",
    "sample": "unknown",
    "protocol": "unknown",
    "sources": [{"label": "原始来源", "url": "https://example.org/review"}],
    "metrics": {
      "weight_g": null, "softness_ac": null, "shock_sa": null,
      "return_pct": null, "forefoot_mm": null, "heel_mm": null, "drop_mm": null
    },
    "use": "用途与往代/变体信息",
    "note": "暂无同口径实验室数据"
  }]
}
```

上例只展示结构；example.org 不是报告证据，执行任务时必须换为真实原始来源。全 null 鞋可用 unknown，并说明缺失；有数值必须有来源、样本与协议。

## 指标口径

| 字段 | 含义 |
| --- | --- |
| weight_g | 相同性别/尺码的单只重量，克 |
| softness_ac | 室温主泡棉 Asker C；越小越软；不与 HA/HC 转换 |
| shock_sa | 后跟吸震，统一实验方法 |
| return_pct | 后跟能量回馈百分比，不直接代表速度或柔软 |
| forefoot_mm / heel_mm | 前掌/后跟鞋底 stack height，包含方法要求的组件 |
| drop_mm | 同来源实测后跟减前掌，无普遍最优值 |

protocol 是实际实验方法标识，sample 是样本/尺码。不同组合在完整图中分块；它们仍可在定性选购图里并列，但不得通过跨方法裸值大小比较得出结论。实验室类别平均值不是该鞋结果；官方参数不能悄悄混进实测列。

RunRepeat 方法入口：https://runrepeat.com/testing-methodology 。执行时读取当前说明。旧文 HA 不换算 AC；部分旧型号可能被回测，按每个字段的真实方法判断，不只看文章日期。抓地、鞋楦、透气等额外指标也必须区分部位、实验方法与量纲。

## 关联规则

- shoes 顺序是原始编号；groups 顺序是两图的类别顺序。
- 每双鞋有唯一 id 和唯一品牌+型号（变体写入型号），只属于一个主组。
- top3 数组顺序就是名次，避免再维护独立 rank 字段。最多三项，必须属于本组，不能重复。
- evidence_urls 必须来自该鞋 sources；需要新增证据时先补来源。
- 少于 min(3,本组鞋数) 个推荐时，给 group.ranking_note 说明证据不足或其他原因。
- 所有正式来源使用直接 HTTP(S) 链接；不使用搜索结果摘要代替读原文。
- 排名不由脚本计算；由执行 skill 的助手先完成证据核验与选购判断。

## 执行与输出

```bash
node scripts/build_shoe_guide.cjs guide.json output
```

Node.js 18+，无 npm 依赖。输出 comparison.svg、top3.svg、sources.html、top3.prompt.txt。SVG 可缩放，显示中文需安装 Noto Sans CJK、思源黑体或系统中文字体。

需要 PNG：在可用浏览器中渲染 SVG 并导出，或使用可用的 SVG 渲染工具；检查字体与裁切后交付。生成式推荐图从 top3.prompt.txt 生成，可把 top3.svg 当排版参考，数值表始终用确定性排版。

代码校验覆盖缺失值、数值范围、坡差关系、ID 关联、来源存在与排名集合；不证明来源真实性或推荐质量，不能代替联网核验和视觉检查。
