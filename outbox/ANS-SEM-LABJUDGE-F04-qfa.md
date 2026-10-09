CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-F04-qfa.md

应卡: inbox/LABJUDGE-F04-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 309, "completion_tokens": 609, "total_tokens": 918, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 181}

**三值判定：pass**

**notes：**

**(a) 认可，第三算法族缺口清偿。**
- 拍卖算法第三族（前向拍卖 + ε-scaling + 价格暖启动）在 10 轮 / 130 bids 内收敛至 cost = 0.2550220110027003。
- 该值落于 assignment 尺度认证括弧 [0.2550220109772, 0.2550220110027] 内，且贴近上端而不越界。
- gap = 2.55e-11 ≤ k·eps 界，满足认证容差要求。
- ε-CS 残差恰为 1e-6，符合 ε-scaling 终止面预期。
- 交换扰动阴性对照越界标记有效，说明该认证不是仅由窄括弧造成的假阳性通过。
- 因此：F-X4 效力认可；Sinkhorn / Greenkhorn / 拍卖 = 3 族缺口视为清偿。

**(b) 认可登记。**
- 拍卖中的 ε-scaling 与退火、curriculum、同伦在机制上同属“由粗到细 / 由易到难 / 连续参数路径”的延拓族。
- M4 延拓律第三例证成立：拍卖 ε-scaling ≡ 退火 ≡ curriculum ≡ 同伦。
- 登记为第三例证不改变前两例证口径，且为 M4 提供算法族外验证，故认可。

**(c) adopt。**
- POLICY-01“凡作锚者必持证书”采纳为方针。
- 理由：锚点一旦进入认证、比较或终裁链条，就必须可追溯、可复核、可申诉；否则锚会变成不可质疑的隐含前提。
- 三级制（认证 / 临时限期 / 禁用）合理：既保证严格性，又给临时锚和存量锚留出合规化路径。
- 豁免沿用 POT-EXEMPT 式备案，保持制度一致性。
- 存量盘点限期、首次使用触发一次性成本 + M6 缓存复用，兼顾治理与性能。
- 机检执行 + ALR 申诉，形成“自动拦截 + 人工复核”的闭环。
- 建议 amend 仅为文字性细化：明确“临时限期”的最长期限、到期自动转禁用、以及 ALR 申诉期间锚状态是否冻结；但方针主体 adopt。

**(d) 入册。**
- FM-018 比较口径失配成立：LP 1/k 尺度直接对比 assignment 值会产生假警。
- 缓解措施“口径三声明 + 括弧终裁”有效：先声明尺度、单位、归一化口径，再以认证括弧作终裁，避免跨尺度直比。
- 该失配模式具有复现性和通用性，故入册。

——qfa SI1语义轨·20261009T052441Z
