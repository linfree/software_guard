import httpx
import json
import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.config import Config
from ..core.config import settings


class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.model_name = self.get_config("ai_model_name", "gpt-3.5-turbo")
        self.base_url = self.get_config("ai_base_url", "")
        self.api_key = self.get_config("ai_api_key", "")
        self.auto_review_enabled = self.get_config("ai_auto_review_enabled", "false").lower() == "true"

    def get_config(self, key: str, default: str = "") -> str:
        """获取配置值"""
        config = self.db.query(Config).filter(Config.key == key).first()
        return config.value if config else default

    async def review_software_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用AI审核软件申请"""
        if not self.auto_review_enabled or not self.base_url or not self.api_key:
            return {"approved": False, "reason": "AI审核未启用或配置不完整"}

        # 构建提示词
        prompt = f"""
        请审核以下软件申请请求，并判断是否批准：
        
        软件名称: {request_data.get('software_name', '')}
        版本: {request_data.get('version', '')}
        下载链接: {request_data.get('download_url', '')}
        描述: {request_data.get('description', '')}
        
        请分析以下方面：
        1. 软件来源是否可信，是否为官方域名，如果是官方直接通过，官方子域名通常也可以。
        2. 是否存在安全风险
        3. 软件连接是否与软件描述一致
        
        请返回JSON格式的结果：
        {{
            "approved": true/false,
            "reason": "审核原因"
        }}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code != 200:
                    return {"approved": False, "reason": f"AI服务错误: {response.status_code}"}

                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 提取可能的JSON代码块
                json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # 如果没有找到代码块，尝试直接解析内容
                    json_str = content.strip()
                
                # 尝试解析AI返回的JSON
                try:
                    review_result = json.loads(json_str)
                    return review_result
                except json.JSONDecodeError:
                    # 如果AI返回的不是有效JSON，使用更严格的关键词检测
                    content_lower = content.lower()
                    has_approved = "approved" in content_lower
                    has_true = "true" in content_lower
                    has_false = "false" in content_lower
                    
                    # 只有同时包含"approved"和"true"且不包含"false"时才通过
                    if has_approved and has_true and not has_false:
                        return {"approved": True, "reason": f"AI自动审核通过：{content}"}
                    else:
                        return {"approved": False, "reason": f"AI审核未通过: {content}"}
                        
        except Exception as e:
            return {"approved": False, "reason": f"AI审核失败: {str(e)}"}