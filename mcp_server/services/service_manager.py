"""
서비스 매니저 - 모든 서비스의 생명주기 관리
"""
import os
from typing import Optional
from .gmail_service import GmailService
from .openai_service import OpenAIService
from .salesforce_service import SalesforceService


class ServiceManager:
    """모든 서비스를 관리하는 매니저 클래스"""
    
    def __init__(self):
        self.gmail: Optional[GmailService] = None
        self.openai: Optional[OpenAIService] = None
        self.salesforce: Optional[SalesforceService] = None
        self._initialized = False
    
    async def initialize(self):
        """모든 서비스를 초기화합니다."""
        if self._initialized:
            return
        
        try:
            # Gmail 서비스 초기화
            self.gmail = GmailService(
                credentials_path=os.getenv("GMAIL_CREDENTIALS_PATH"),
                token_path=os.getenv("GMAIL_TOKEN_PATH", "token.json")
            )
            await self.gmail.initialize()
            
            # OpenAI 서비스 초기화
            self.openai = OpenAIService(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            # Salesforce 서비스 초기화
            self.salesforce = SalesforceService(
                username=os.getenv("SALESFORCE_USERNAME"),
                password=os.getenv("SALESFORCE_PASSWORD"),
                security_token=os.getenv("SALESFORCE_SECURITY_TOKEN"),
                domain=os.getenv("SALESFORCE_DOMAIN", "login")
            )
            await self.salesforce.initialize()
            
            self._initialized = True
            print("✅ 모든 서비스가 초기화되었습니다.")
        
        except Exception as e:
            print(f"❌ 서비스 초기화 실패: {e}")
            raise
    
    async def cleanup(self):
        """리소스를 정리합니다."""
        if self.gmail:
            await self.gmail.cleanup()
        if self.salesforce:
            await self.salesforce.cleanup()
        
        self._initialized = False
        print("✅ 모든 서비스가 정리되었습니다.")