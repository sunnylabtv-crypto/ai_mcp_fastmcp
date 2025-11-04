"""
MCP 서버 기능 테스트
"""
import asyncio
from mcp_server.server import (
    fetch_unread_emails,
    analyze_email_with_ai,
    create_salesforce_lead
)


async def test_workflow():
    """전체 워크플로우 테스트"""
    
    # 1. 이메일 가져오기
    print("📧 이메일 가져오는 중...")
    emails_result = await fetch_unread_emails(max_results=5)
    print(f"결과: {emails_result}")
    
    if emails_result["success"] and emails_result["count"] > 0:
        first_email = emails_result["emails"][0]
        
        # 2. AI 분석
        print("\n🤖 AI 분석 중...")
        analysis_result = await analyze_email_with_ai(
            first_email["snippet"],
            "customer_inquiry"
        )
        print(f"결과: {analysis_result}")
        
        # 3. Salesforce 리드 생성
        print("\n💼 Salesforce 리드 생성 중...")
        lead_data = {
            "first_name": "Test",
            "last_name": "Customer",
            "email": "test@example.com",
            "company": "Test Company"
        }
        lead_result = await create_salesforce_lead(lead_data)
        print(f"결과: {lead_result}")


if __name__ == "__main__":
    asyncio.run(test_workflow())