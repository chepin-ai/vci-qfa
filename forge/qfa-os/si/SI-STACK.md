# SI-STACK-01 — qfa 线层栈规约

## 层职
- SI1 会话层：拍令解析、野问册维护、判词初裁、场链播种
- SI5 机器层驱动：git/REST 双轨、FRAG 扫描、books-keeper/forge 工作流发起、回执验讫（receipt-first）

## 链式（可复算，凡锚必可复算）
- canon(c)=json.dumps(c, ensure_ascii=False, sort_keys=True, separators=(',',':'))
- capsule: cap_hash = sha256(prev_cap_hash + canon(cap sans cap_hash))[:16]
- wm: hash = sha256(prev_wm_hash + canon(wm sans hash))[:16]
- field chain: entry {prev,ver,ts,by}; hash = sha256(prev + canon(entry))[:16]
- 文件字节锚 = sha256(bytes)[:16]（自嵌锚禁用——beat-123 教训）

## 判词律 v2
双基线：经典基线（BP-03 精确值）+ 资源轴分开声明；[全证]/[借证]/[机验]/[未证] 四档判词。

## 迭诫（至 beat-126）
1-6 见前账。七：数值平台 ≠ 上界——下界方法停滞不构成「无优势」证据；凡涉无优势判词，构造性反例扫描先行（beat-125 see-saw 0.75 平台被反例击破实证）。
