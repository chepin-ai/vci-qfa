CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-WILDQ-MONOTONE-01-qfa.md

应卡: inbox/WILDQ-MONOTONE-01-qfa.md
引擎: 〈RED〉/deepseek-chat usage={"prompt_tokens": 394, "completion_tokens": 2317, "total_tokens": 2711, "prompt_tokens_details": {"cached_tokens": 256}, "prompt_cache_hit_tokens": 256, "prompt_cache_miss_tokens": 138}

先直接给判断：**枢案 v0 的 M 作为“联邦级非刚性度/治理债标量”是可用的首测指标，但还不是严格的单调性公式。** 它现在混了三类东西：真正沿波次单调的“未闭环债”、会因 fail-open/缺 fp 等事件跳变的“事故计数”、以及 ask 是否自包含这类“格式/可评审性”指标。若不做分层，M1 的“非增”在联邦级会被波次边界上的新 ask、新 finding、fail-open 事件破坏；M2 的“M_line=0 ⇔ 可升级刚性态”也过强，需要加“无未决依赖、无外部输入、评审双轮完成、制品自包含可重放”等条件。

---

## A) 线-local 单调量 M_line

对一条线，建议把 M_line 定义成**沿“闭环进度/证据完备度”单调不增的债量**，而不是沿时间或波次单调。

一个可用的线-local 候选：

\[
M_{\text{line}}
=
w_u |U|
+
w_f |F_{\text{open}}|
+
w_c |C_{\text{missing}}|
+
w_r |R_{\text{unresolved}}|
+
w_a |A_{\text{non-self-contained}}|
\]

其中：

- \(U\)：线内 undecided 节点/问题；
- \(F_{\text{open}}\)：线内 fail-open 事件，但只计“尚未被负结果入册闭环”的；
- \(C_{\text{missing}}\)：应闭环但未闭环的 FINDING / contradiction / counterexample；
- \(R_{\text{unresolved}}\)：未解决的依赖、外部输入、上游 ask；
- \(A_{\text{non-self-contained}}\)：非自包含 ask / 不可独立重放的制品。

权 \(w_i>0\)。

### 沿何参数单调？

沿**闭环算子 \(Cl\) 的迭代次数**单调不增，而不是沿波次单调。

定义闭环算子：

\[
Cl(X)=X \cup \{\text{已入册的负结果、已闭环 FINDING、已补 fp、已转自包含的 ask}\}
\]

若每步只允许：

1. 把 undecided 变为 decided 或明确标记 undecided；
2. 把 fail-open 事件转为已入册负结果；
3. 把未闭环 FINDING 闭环；
4. 补 fp 卡件；
5. 把非自包含 ask 改写为自包含 ask；

则：

\[
M_{\text{line}}(Cl(X)) \le M_{\text{line}}(X)
\]

等号成立当且仅当这一步没有减少任何上述未闭环项，或者减少量被新增同权项抵消。

### 等号集

\(M_{\text{line}}=0\) 的等号集应解释为：

\[
U=\varnothing,\quad F_{\text{open}}=\varnothing,\quad C_{\text{missing}}=\varnothing,\quad R_{\text{unresolved}}=\varnothing,\quad A_{\text{non-self-contained}}=\varnothing
\]

即：

- 线内无 undecided；
- 无未闭环 fail-open；
- 无未闭环 FINDING；
- 无未解决依赖；
- 无非自包含 ask。

这时线-local 达到**可升级刚性态候选**。

但注意：这只是候选，不等于自动可升级。还需要评审双轮、版本闸门、无外部未决输入等。

### 与枢案 M 的关系

建议关系是：

\[
M_{\text{fed}} \ge \sum_{\text{line}} M_{\text{line}}
\]

或者更准确：

\[
M_{\text{fed}}
=
\sum_{\text{line}} M_{\text{line}}
+
M_{\text{cross}}
+
M_{\text{meta}}
\]

其中：

- \(M_{\text{cross}}\)：跨线未闭环依赖、跨线 ask、跨线 FINDING；
- \(M_{\text{meta}}\)：联邦级 fail-open、无 fp 卡件、非自包含 ask、治理级 undecided。

因此：

- \(M_{\text{line}}\) 是 \(M_{\text{fed}}\) 的子项，但不是简单子项，因为联邦级还有跨线和元级债；
- \(M_{\text{line}}\) 可以独立定义、独立单调；
- 反例是：所有线 \(M_{\text{line}}=0\)，但 \(M_{\text{fed}}>0\)，因为跨线依赖未闭环或联邦级 fail-open 未入册。

所以：**M_line 是 M_fed 的下界分量，不是等价分量。**

---

## B) 对枢案 M 的反例或修正

有反例。

### 反例 1：M=0 但不可升级

构型：

- 所有 undecided 被标记为 decided，但其实是“假 decided”，没有负结果入册；
- fail-open 事件为 0，因为没有记录；
- FINDING 为 0，因为没开；
- 无 fp 卡件为 0，因为没检查；
- 非自包含 ask 为 0，因为 ask 被删了。

此时：

\[
M=0
\]

但线不可升级，因为：

- 没有负结果入册；
- 没有双轮评审；
- 没有可重放制品；
- 没有 fp 卡件支撑。

所以 M=0 不充分。

修正：M=0 只能推出“在当前可观测项上无债”，不能推出“可升级刚性态”。必须加：

\[
M=0 \land \text{双轮评审完成} \land \text{负结果入册完整} \land \text{制品自包含可重放}
\]

才可升级。

---

### 反例 2：M>0 但已刚性

构型：

- 某线已经通过双轮评审，进入刚性态；
- 但联邦级还有一个无关线的 undecided；
- 或者有一个历史 fail-open 事件已闭环，但仍被计入 \(F_{\text{open}}\)；
- 或者有一个非自包含 ask 已被标记为“豁免”，但没从 M 中扣除。

此时：

\[
M>0
\]

但该线已刚性。

所以 M 的“非零”不自动推出“非刚性”。M 是全局债标量，不是刚性判定位。

修正：需要区分：

- \(M_{\text{blocking}}\)：真正阻断升级的债；
- \(M_{\text{non-blocking}}\)：已闭环、已豁免、历史记录、非本线债。

只有 \(M_{\text{blocking}}=0\) 才与可升级相关。

---

### 反例 3：M 沿波次非增不成立

波次边界会引入新 ask、新 finding、新 fail-open。若第 \(k+1\) 波新开一个 FINDING，则：

\[
M_{k+1} > M_k
\]

即使各波守三即律和负结果入册。

所以 M1 的“沿波次非增”只在**同一闭环算子迭代下**成立，不在“波次推进”下自动成立。

修正：

- 把 M1 改为：沿闭环算子 \(Cl\) 非增；
- 波次推进时允许 M 暂时增加，但要求新增项最终被闭环；
- 或者定义“收尾波”为 M 严格增的波，则产物滞留 v1-draft，升级锁死。这与推论 M3 一致。

---

### M 缺哪一项？

至少缺四项：

1. **阻断性/非阻断性分层**  
   需要 \(M_{\text{blocking}}\) 与 \(M_{\text{non-blocking}}\)。

2. **闭环完整性/负结果入册质量**  
   现在只计“未闭环 FINDING”，但没计“假闭环”“未入册负结果”。

3. **评审状态**  
   M2 需要“双轮律”，但 M 本身没有评审项。应加：
   \[
   \eta |\text{未完成双轮评审}|
   \]

4. **自包含/可重放性**  
   现在只计“非自包含 ask”，但还应计“制品不可独立重放”“依赖外部未决输入”。

5. **跨线/联邦级债**  
   M_line 与 M_fed 需要显式区分，否则线级 M=0 会被联邦级债掩盖。

---

## 修正后的枢案 M 建议

\[
M_{\text{fed}}
=
M_{\text{blocking}}
+
M_{\text{non-blocking}}
\]

其中：

\[
M_{\text{blocking}}
=
\alpha |U_b|
+
\beta |F_{\text{open},b}|
+
\gamma |C_{\text{missing},b}|
+
\delta |FP_{\text{missing},b}|
+
\epsilon |A_{\text{non-self-contained},b}|
+
\eta |R_{\text{review incomplete}}|
+
\theta |D_{\text{cross-line unresolved}}|
\]

\[
M_{\text{non-blocking}}
=
\alpha' |U_{\text{closed}}|
+
\beta' |F_{\text{closed}}|
+
\gamma' |C_{\text{closed}}|
+
\cdots
\]

升级条件：

\[
M_{\text{blocking}}=0
\land
\text{双轮评审完成}
\land
\text{负结果入册完整}
\land
\text{制品自包含可重放}
\]

这样：

- M1 可改为：沿闭环算子，\(M_{\text{blocking}}\) 非增；
- M2 可改为：\(M_{\text{blocking}}=0\) 且评审/入册/自包含条件满足，才可升级刚性态；
- M3 可保留：波次使 \(M_{\text{blocking}}\) 严格增 ⇒ 非收尾波，升级锁死。

---

## 结论

- **A)** 线-local 单调量应沿闭环算子单调不增；等号集是线内无未闭环债；它是枢案 M 的下界分量，不是等价分量。
- **B)** 枢案 M 有反例：M=0 未必可升级，M>0 未必非刚性；M1 沿波次非增不成立，只沿闭环算子成立。M 缺阻断/非阻断分层、评审状态、闭环质量、自包含可重放、跨线债。修正后可作为 v1-draft 的治理指标，但 v1 刚性闸门不能只看原始 M=0。

——qfa SI1语义轨·20261007T153328Z
