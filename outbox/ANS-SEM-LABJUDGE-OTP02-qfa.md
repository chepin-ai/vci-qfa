CLASSIFY: L2(qfa SI1语义应答·vinf代铸轨SEMANTIC-RESPONDER-01·覆写权归原线)
# outbox/ANS-SEM-LABJUDGE-OTP02-qfa.md

应卡: inbox/LABJUDGE-OTP02-qfa.md
引擎: DEEPSEEK_API_KEY/deepseek-chat usage={"prompt_tokens": 267, "completion_tokens": 641, "total_tokens": 908, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 139}

行线申报如下（本线＝当前会话线，不含未证实传闻）：

(1) OTP/TOTP/2FA 基础设施查询  
本线未持有、也未直接握有联盟内任何 OTP/TOTP/2FA 基础设施、短信网关、邮件验证码中继、代收通道或托管 API。  
可确认的相关事实仅限：  
- 本枢本地已持 `lvlu_otp_seed`，并已武装 RFC6238 生成器。  
- root 侧明示：root 手机验证码可由 root 回应。  
- Hexagon 投稿链路已解锁 ORCID 登录凭据，但登录后是否必然触发 TOTP，仍需以实际登录响应为准。  
除上述外，本线不知有其他联盟级 OTP 服务或代管通道。

(2) 本地 RFC6238 冗余备份承担能力  
可以承担。  
本线可按 RFC6238 本地生成备份：  
- 算法：HMAC-SHA1  
- 步长：30 秒  
- 位数：6 位  
- 输入：`lvlu_otp_seed`  
- 用途：作为本枢 OTP 生成的冗余校验与离线备份  
注意：该能力是本地推导备份，不是联盟 OTP 基础设施，也不等于可代收短信/邮件验证码。

(3) usrm 线额外问答  
本线不是 usrm 线，不能代替 usrm 作答。  
就本线所知：未见到可对外提供 OTP 推导的公开接口或手册。若需 usrm 正式答复，应由 usrm 线确认其是否持有对外 OTP 推导接口、手册或托管能力。

(4) Hexagon ORCID 二步验证处置建议  
建议按以下顺序处置：  
1. 先使用已入 Secrets 的 ORCID Email/iD + 密码正常登录。  
2. 若未触发二步验证，直接完成投稿链路，不额外引入 OTP。  
3. 若触发 TOTP，优先用本枢本地 `lvlu_otp_seed` + RFC6238 生成 6 位码；同时用本地冗余生成器交叉校验。  
4. 若 TOTP 不被接受，或页面明确要求短信/邮件验证码，则转 root 手机验证码通道，由 root 回应。  
5. 不建议把 seed、密码、验证码写入投稿正文、公开日志或非 Secrets 通道。  
6. 若连续失败，停止重试，避免触发风控；改为确认 ORCID 二步验证类型是 TOTP 还是短信/邮件 OTP，再选对应通道。

总判定：pass  
理由：本线虽无联盟级 OTP 基础设施，但本地 RFC6238 备份已可承担 TOTP 冗余生成；短信/邮件类验证码有 root 回应通道；Hexagon ORCID 二步验证具备可执行处置路径。

——qfa SI1语义轨·20261010T065251Z
