CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-EXEC-QFA-01.md

应卡: inbox/WILDQ-EXEC-QFA-01.md
引擎: 〈RED〉/kimi-k3 usage={"prompt_tokens": 334, "completion_tokens": 2272, "total_tokens": 2606, "completion_tokens_details": {"reasoning_tokens": 1436}, "prompt_tokens_details": {"cache_write_tokens": 256}}

【互锚验】本run亲读vci-vinf链尖fp=**81a9234bdff61b99**(源:TIP-349-81a9234bdff61b99.json)。**诚实缺口①**:来卡WILDQ-EXEC-QFA-01.md未随令附fp,无法比对一致性,记缺口待补锚,不阻塞交付。

因全文过长,按令给骨架+三段核心规则+判据段。

## 1. tower_contract.yaml(骨架)

```yaml
contract: tower_contract/v1
towers:
  - {id: T-A, scope: ["data/*"],   priority: 1, writers: [svc-data]}
  - {id: T-B, scope: ["policy/*"], priority: 2, writers: [svc-policy]}
  - {id: T-C, scope: ["obs/*"],    priority: 3, writers: [svc-obs]}
conflict:
  total_order: "priority asc → lamport asc → writer_id lex asc"  # 全序,可复现
  quorum: "2/3"
write_guard: {require_capability: true, scope_enforcement: strict}
rollback: {mode: inverse-op-replay, order: reverse, idempotent: true}
audit: {append_only: true, hash_chain: "sha256(prev_hash||entry)"}
```

## 2. arbiter_api(骨架)

```python
class Arbiter:
    def submit(self, op: Op, cap: Capability) -> Receipt: ...
    def arbitrate(self, ops: list[Op]) -> Decision: ...   # R1
    def write_guard(self, op: Op, cap: Capability) -> Allow|Deny: ...  # R2
    def rollback(self, op_id: str) -> RollbackReceipt: ...  # R3
```

## 3. 三段核心规则

**R1 冲突仲裁**:同刻多塔写同键→按contract全序选唯一胜方;败方置CONFLICT_REJECTED;决策+输入指纹写入audit,重放同输入必得同结果(确定性,禁随机/墙钟)。

**R2 越权拒写**:写前双检——capability有效 ∧ key∈writer.scope;任一失败→DENY,状态零变更,负结果立即入册(三即律),返回Deny(reason, audit_seq)。

**R3 回滚可复现**:每笔写落盘前生成inverse_op;rollback(op_id)=按audit逆序重放逆操作,幂等(重放N次同态);日志哈希链保证可校验、不可篡改。

## 4. 验证判据段

```yaml
acceptance:
  C1: "三塔同刻冲突写→唯一胜方,败方REJECTED,audit含ARBITRATE记录;连跑100次结果全同"
  C2: "无cap或越scope写→DENY,state_hash不变,audit含REJECT负结果条目"
  C3: "rollback(op_id)后state_hash==op前快照hash;二次rollback不报错且态不变"
  C4: "pytest tests/e2e 全绿(C1-C3用例)"
```

## 5. 自验声明

- C1/C2/C3:**设计层满足**(规则R1-R3与骨架对应,判据可机读),但未经运行验证。
- C4:**不满足,点名**——本run无执行环境,e2e测试未跑,按负结果入册登记:`{type: NEGATIVE, item: C4, cause: no-exec-env}`。不得自称"端到端通过"。
- 缺口①(来卡fp缺失)未闭合。二者补齐前,本交付物状态=**草案v1-draft**,不升级名。

——qfa SI1语义轨·20261003T160749Z
