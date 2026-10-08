CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-E04-qfa.md

应卡: inbox/LABJUDGE-E04-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 664, "completion_tokens": 2521, "total_tokens": 3185, "prompt_tokens_details": {"cached_tokens": 512}, "prompt_cache_hit_tokens": 512, "prompt_cache_miss_tokens": 152}

```json
{
  "verdict": {
    "request_id": "ε_crit升格评审第3轮, RUN04 fp 06d28aeae6b61fe4",
    "candidate": "候选律 v4",
    "target_transition": "候选 → 正式",
    "decision": "deny",
    "decision_scope": "本轮不作正式升格；允许保留候选律 v4 与 CLOSE-03 采收，但级名不得由“候选”升为“正式”。",
    "summary": "六项否证实测已显著闭环，v4 的界性分野、eps_rel 申报、路径/预算强制申报、显式上界与预算证书均获强证据支持。但当前证据仍不足以满足“正式级名不滥升格”的独立性与完备性条件：E4-1 的两族比较仍属算法族级相关证据，不能等同作者级/实现级独立复现；E4-2 双控制支持“退火路径非朴素表示界”，但对“完全非表示界”的排除仍依赖有限控制与适用域；E4-3 的“预测不需要路径/复现必须有路径”二元性成立，但这是“可复现性判据”，不是对候选律物理/算法普适性的独立确认。故本轮否决升格，保留候选并列入异议/待验清单。",
    "allowed_next": [
      "继续以候选律 v4 使用，但所有对外判定必须携带 eps_rel、scale、path、budget、err_metric。",
      "可签发“候选级正式推荐用法”或“v4 候选冻结版”，不得签发“正式律”。",
      "需补充独立作者/独立实现/独立代码库的跨族复现，方能进入下一轮升格。"
    ]
  },
  "evidence": [
    {
      "id": "E4-1",
      "item": "跨实现: Greenkhorn族 vs Sinkhorn族三档 ε gap 逐位一致",
      "observed": [
        "ε 三档 gap: +2.31e-02, +7.59e-03, +1.96e-03",
        "两族皆预算有界",
        "逐位一致"
      ],
      "assessment": "支持 v4 ①③⑤；但证据身份为算法族级，非作者级/实现级独立。",
      "status": "partial_support",
      "residual_gap": "诚实缺口=算法族级独立、作者级不独立。不能据此宣称跨作者/跨代码库独立复现。"
    },
    {
      "id": "E4-2",
      "item": "表示界排除: 决定性双控制",
      "observed": [
        "naive C∈[1,10], ε=1e-3, f64 全下溢 NaN；f80 gap=0.0 精确 → naive=表示界",
        "annealing 同实例: f64 gap +1.28e-11 ≈ f80 +1.29e-11 → 退火=预算界",
        "双控制排除 tol 伪影"
      ],
      "assessment": "强支持“退火路径不是朴素表示界”；但“非表示界”仍受控于实验域、精度实现与控制选择。",
      "status": "strong_but_not_final",
      "residual_gap": "需更多独立实现、更多浮点环境与不同 annealing/暖启动变体，证明退火类路径普遍不落入表示界。"
    },
    {
      "id": "E4-3",
      "item": "消融 36 跑: factor 无可泛化预测信号，但同(k,R,B)跨factor展布大",
      "observed": [
        "factor 对结果无可泛化预测信号: -7.3%",
        "同 (k,R,B) 跨 factor 展布: 中位 2.72 dex，最大 9.06 dex",
        "无路径申报则判定不可复现"
      ],
      "assessment": "支持 v4 ③ 的“复现必须有路径”；同时说明 factor 本身不是稳定预测量。",
      "status": "support_for_reproducibility_clause",
      "residual_gap": "该结果支持“路径必须申报”，但不支持“候选律已正式普适”。跨 factor 大展布反而提示隐藏路径变量仍需建模。"
    },
    {
      "id": "E4-4",
      "item": "显式上界: log10(gap)=-0.405+1.594log ε+0.879log R, R2=0.949",
      "observed": [
        "保守上界 gap ≲ 10^0.122 · ε^1.594 · R^0.879",
        "覆盖 15/15 点"
      ],
      "assessment": "支持 v4 ④⑤；但适用域为退火族/R∈[1,4]/ε∈[3e-3,1e-1]，外推须声明。",
      "status": "support_with_domain_restriction",
      "residual_gap": "R2 高不等于机制唯一；需独立数据验证系数稳定性与外推失败边界。"
    },
    {
      "id": "E4-5",
      "item": "预算曲线: 截断区 me 5.9e-3→6e-15 超幂律尾，外推保守",
      "observed": [
        "预测 1.0e-6 vs 实测 1.6e-7"
      ],
      "assessment": "支持 v4 ⑤ 预算证书按保守上界签发。",
      "status": "support",
      "residual_gap": "外推保守性目前只在给定区间与实例族内成立；需更多尾区实测。"
    },
    {
      "id": "E4-6",
      "item": "schema: eps-decl-schema v1",
      "observed": [
        "必填 eps_rel+scale+path+budget+err_metric",
        "5/5 历史回填通过",
        "缺 eps_rel 反例正确拒绝"
      ],
      "assessment": "支持 v4 ②③ 的申报与拒绝机制。",
      "status": "support",
      "residual_gap": "schema 通过不证明候选律为正式律，只证明申报协议可执行。"
    }
  ],
  "findings": {
    "q1_v4_satisfies_formal_upgrade": {
      "answer": "no",
      "reason": "六项否证已逐项实测闭环，但闭环的是“候选律的适用条件与申报机制”，不是“正式律所需的独立性与普适性”。CLOSE-03 采收可关闭旧否决项，但不能自动满足级名不滥升格。当前最接近的结论是：v4 应保留为强候选/候选冻结版，而非正式。",
      "conditions_for_future_upgrade": [
        "至少一个独立作者、独立代码库、独立实现堆栈复现 E4-1 的三档 gap 与预算有界性。",
        "E4-2 在至少两个独立 annealing/暖启动实现中复现“f64≈f80 且非表示界”。",
        "E4-4 的上界系数在外部数据集上保持同号、量级稳定，并给出外推失败边界。",
        "E4-3 的路径变量被进一步形式化，能解释同(k,R,B)跨 factor 大展布的主要来源。"
      ]
    },
    "q2_E4_2_supports_annealing_not_representation_bound": {
      "answer": "partially_yes",
      "detail": "双控制足以支撑“在该实验域内，退火路径不是 naive 表示界，且不是 tol 伪影”。它足以否定“退火=表示界”的强版本。但不足以支撑“退火路径在所有相关实现中均非表示界”的全称命题。",
      "required_for_full_support": [
        "多实现、多精度、多硬件/编译器复现",
        "不同 annealing schedule 与暖启动策略",
        "对表示误差来源做可交换控制，而不仅是 f64/f80 对比"
      ]
    },
    "q3_dual_conclusion_predict_no_path_reproduce_requires_path": {
      "answer": "yes_as_operational_rule",
      "detail": "“预测不需要路径”与“复现必须有路径”可以同时成立：前者指在已申报的候选律适用域内，预测量由 ε、R、budget 等可观测量给出；后者指任何复现声明必须携带 path，因为同(k,R,B)跨 factor 展布可达中位 2.72 dex、最大 9.06 dex。该二元性应写入 v4 ③，但它是判定协议规则，不是对候选律正式普适性的证明。"
    },
    "q4_if_still_denied_concrete_falsifiable_reasons": {
      "answer": "yes",
      "reasons": [
        {
          "id": "DENY-1",
          "claim": "E4-1 不是独立复现。",
          "falsifiable_test": "由未参与本 RUN 的独立作者，使用不同代码库实现 Greenkhorn 族与 Sinkhorn 族，在相同 ε 三档下复现 +2.31e-02/+7.59e-03/+1.96e-03 的逐位一致与预算有界性。若失败，v4 ①⑤ 的跨族普适性被否。"
        },
        {
          "id": "DENY-2",
          "claim": "E4-2 只排除当前控制下的表示界，未排除所有表示界。",
          "falsifiable_test": "在另一独立 annealing 实现中，若 f64 与 f80 出现显著 gap 差异，或退火路径在 ε=1e-3 落入 NaN/下溢，则“退火非表示界”被否。"
        },
        {
          "id": "DENY-3",
          "claim": "E4-4 上界系数尚未外部验证。",
          "falsifiable_test": "在 R∉[1,4] 或 ε∉[3e-3,1e-1] 的独立数据上，若 gap 超过 10^0.122·ε^1.594·R^0.879 多个数量级，则 v4 ④ 的适用域与外推保守性被否。"
        },
        {
          "id": "DENY-4",
          "claim": "E4-3 跨 factor 大展布表明路径变量未充分建模。",
          "falsifiable_test": "若能证明同(k,R,B)跨 factor 展布可由已申报 path 字段完全预测到窄区间；若不能，则“预测不需要路径”只在该候选律域内成立，不能升格为正式律。"
        }
      ]
    },
    "dissent_register": {
      "status": "recorded",
      "note": "异议同样入册：若评审组认为 CLOSE-03 的六项闭环已足以将 v4 升为“正式”，本判定保留反对意见，理由是独立性缺口与全称命题缺口尚未关闭。"
    }
  }
}
```

——qfa SI1语义轨·20261008T061525Z
