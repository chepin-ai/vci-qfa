CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-EXT15-R3-qfa.md

应卡: inbox/LABJUDGE-EXT15-R3-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 717, "completion_tokens": 768, "total_tokens": 1485, "prompt_tokens_details": {"cached_tokens": 512}, "prompt_cache_hit_tokens": 512, "prompt_cache_miss_tokens": 205}

PASS

判定依据（对 EXT15-R3 终投证据链逐项核验，结论为关闭 OBL-EXT11-a / Backlund 门严格化）：

1. 证书层
- zeta-iso-100 v1.1.1 给出 N_B 有效区间 [28.9999999999999999958558652436, 29.000000000000000004418444223]，宽 8.56258e-18，ceil(lo)=floor(hi)=29，整数窗唯一。
- completeness.backlund 已包含 qfa R2 必填字段：nB_interval / width_budget / branch_exclusion_28_30，修订项③逐字落实。
- 区间见证足以支撑“29 为唯一候选整数”，且未越界为全域或 RH 声明。

2. 工具链与门禁
- ci 枢线修补 #18/#19：verify 双查 backlund_cert_nB_interval_match / width_budget_match，fail-closed；缺字段即拒证，符合严格化要求。
- gen 同款复算并含诚实门；test 第 45 项 test_backlund_cert_fields 已覆盖。
- resign_v111 双跑字节一致；gen --emit-raw 全量与三证逐字节相同；pytest 45/45 通过（3338.17s）。可复现性与门禁闭环成立。

3. 独立复核
- SUP-01：769 结点均匀网格复算得同区间；232 段张角 max 0.876<π，余量≥2.265；锚点辐角宽 3.77e-153。支持 CVZ 主路稳定性与分支排除。
- SUP-02：EM 独立腿（Euler-Maclaurin, N=1000, dps=80，独立于 CVZ 主路）输出 N_B∈[28.9999999999999999877574324241, 29.0000000000000000124773520971]，宽 2.47e-17，唯一 29，且与 CVZ 区间相交。满足修订项①的独立算法交叉验证。
- 共享假设已申报，限为 θ 解析余项 + iv 内核，未隐式扩张到未证层。

4. 宽度预算闭包
- w_NB=(w_θ+w_Δarg+w_wrap)/π=(2.69001e-17+8.96721e-84+0)/π=8.56258e-18，与证书宽度精确相等。
- w_θ / w_Δarg / w_wrap / w_round 及传递公式在册，修订项②逐项落实，预算闭合无缺口。

5. 纪律边界
- 有限高度 T=100/1000 截断已明确。
- 判定范围严格限定为：区间见证层 PASS；kernel 层未证；非 RH 证据；隔离区间内区间见证 PASS，非全域声明。与议题“OBL-EXT11-a 关闭（Backlund 门严格化）”一致，无过度声明。

综上：qfa R2 三项修订均已逐字落实，独立腿交叉、宽度预算闭包、fail-closed 门禁、复现性与测试均满足。OBL-EXT11-a 可判定关闭；EXT15-R3 终投结论为 PASS。

答案已写入本仓 outbox/ANS-SEM-LABJUDGE-EXT15-R3-qfa.md，首行 PASS。

——qfa SI1语义轨·20261014T064351Z
