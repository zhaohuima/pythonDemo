# 🔧 API 错误处理改进说明

## 问题描述

在测试时遇到错误：
```
[14:43:57] Execution failed: LLM API call failed (HTTP 500): 
{"code":60009,"message":"Request processing failed due to an unknown error.","data":null}
```

## 问题原因

HTTP 500 错误是服务器端临时错误，可能由以下原因引起：
1. API 服务器临时过载
2. 网络波动
3. 服务端处理异常
4. 模型服务暂时不可用

**原代码问题**：遇到 HTTP 500 错误时直接失败，没有重试机制。

## 改进内容

### 1. 智能重试机制

现在代码会对以下错误进行自动重试：
- **HTTP 500-599**（服务器错误）- 自动重试
- **HTTP 429**（限流）- 自动重试
- **超时错误** - 自动重试
- **网络错误** - 自动重试

### 2. 指数退避策略

重试间隔采用指数退避：
- 第 1 次重试：等待 2 秒
- 第 2 次重试：等待 4 秒
- 第 3 次重试：等待 6 秒

避免频繁请求导致服务器压力更大。

### 3. 详细错误日志

改进的错误日志包含：
- HTTP 状态码
- API 错误代码（如 60009）
- 错误消息
- 重试次数和状态

### 4. 错误分类处理

- **服务器错误（5xx）**：自动重试
- **限流错误（429）**：自动重试
- **客户端错误（4xx，除429）**：不重试，直接失败
- **超时错误**：自动重试

## 代码改进

### 改进前
```python
except httpx.HTTPStatusError as e:
    logger.error(f"LLM API call failed (HTTP {e.response.status_code}): {e.response.text}")
    raise Exception(f"LLM API call failed (HTTP {e.response.status_code}): {e.response.text}")
```

### 改进后
```python
except httpx.HTTPStatusError as e:
    status_code = e.response.status_code
    
    # 解析错误响应
    error_json = e.response.json()
    error_code = error_json.get("code", "unknown")
    error_msg = error_json.get("message", error_text)
    
    # 服务器错误和限流错误：自动重试
    if status_code >= 500 or status_code == 429:
        # 指数退避重试
        wait_time = 2 * (attempt + 1)
        time.sleep(wait_time)
        continue
    else:
        # 客户端错误：不重试
        raise Exception(...)
```

## 使用效果

### 改进前
- HTTP 500 错误 → 立即失败
- 用户需要手动重试
- 无法处理临时性错误

### 改进后
- HTTP 500 错误 → 自动重试 3 次
- 每次重试间隔递增（2s, 4s, 6s）
- 大部分临时错误可以自动恢复
- 详细的错误日志便于排查

## 测试建议

1. **正常情况**：应该能正常处理请求
2. **临时错误**：HTTP 500 错误会自动重试
3. **持续错误**：如果 3 次重试都失败，会显示详细错误信息

## 如果仍然遇到错误

### 1. 检查 API 密钥
```python
# 在 config.py 中检查
API_KEY = "sk-..."
```

### 2. 检查 API 端点
```python
API_BASE_URL = "https://api.siliconflow.cn/v1"
```

### 3. 检查模型名称
```python
MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
```

### 4. 查看详细日志
在 EC2 上：
```bash
sudo journalctl -u product-master -f
```

或查看应用日志：
```bash
tail -f ~/ProductMaster/logs/product_master_$(date +%Y%m%d).log
```

### 5. 联系 API 服务商
如果错误持续出现，可能是 API 服务端问题，需要联系硅基流动技术支持。

## 常见错误代码

| 错误代码 | 说明 | 处理方式 |
|---------|------|---------|
| 60009 | 服务器未知错误 | 自动重试 |
| 429 | 请求频率过高 | 自动重试（等待更长时间） |
| 401 | 认证失败 | 检查 API 密钥 |
| 400 | 请求参数错误 | 检查请求格式 |
| 503 | 服务不可用 | 自动重试 |

## 监控建议

建议监控以下指标：
- API 调用成功率
- 重试次数
- 平均响应时间
- 错误类型分布

---

**更新日期**: 2026-01-08
**版本**: 1.1.0
