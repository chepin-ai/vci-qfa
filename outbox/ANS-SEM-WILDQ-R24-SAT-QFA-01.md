CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-R24-SAT-QFA-01.md

应卡: inbox/WILDQ-R24-SAT-QFA-01.md
引擎: KIMI_API_KEY/kimi-k2.6 usage={"prompt_tokens": 253, "completion_tokens": 2286, "total_tokens": 2539, "completion_tokens_details": {"reasoning_tokens": 1887}}

【互锚验】fp=81a9234bdff61b99，与来卡TIP-349源fp一致。

Q1：账册条目schema统一定为六元组`(dtype, blake3_fp, lineage_prev, sig, ts, mmr_idx)`。预印本PDF先抽页级SHA3-512再求Merkle根；全文文本经NFKC归一化与空白规范化后取BLAKE3；技能仓commit登记原git-sha256并附tree-hash做血缘；未来Lean源按模块级AST哈希+环境常量hash登记。指纹锚定协议采用线性MMR：每制品fp作为叶节点，批次峰顶哈希写入books-keeper-01轨的tip锚点，实现跨轨不可篡改。

Q2：审计门四层（采/洗/裁/存）日志本身即制品，每层输出立即BLAKE3化，通过books-keeper-01的`audit_ingest`接口写入独立shard。对接协议为双向epoch锚定：QFA-SI1每epoch提交四层合并MMR根，books-keeper-01回写带时间戳的签认哈希；若校验不符，异常直接以负结果条目追加至`neg_outcome`分册，确保审计日志的审计链同样append-only且可追责。

Q3：Lean复算潮多线并发写时，append-only账册禁止merge-rebase。冲突裁决：①以形式校验完成位为主键，时戳为辅；②若时戳撞车，取内容BLAKE3字典序较小者入主链；③其余分叉作为`fork_ref`侧枝追加，标记`superseded`并回指主链条目；④凡形式校验未通过者，无论先后均入`neg_outcome`册。主链始终保持单调递增，级名不滥，负结果亦留痕。

——qfa SI1语义轨·20260929T102736Z
