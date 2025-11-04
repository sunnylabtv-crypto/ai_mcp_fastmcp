"""
Sales Assistant MCP Server
Claude AI가 자연어로 명령하면 자동으로 Gmail, OpenAI, Salesforce 기능을 실행
"""
import os
import asyncio
from typing import Optional
from fastmcp import FastMCP
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# FastMCP 서버 초기화
mcp = FastMCP("Sales Assistant", dependencies=["python-dotenv"])

# 서비스 매니저 (기존 코드 활용)
from .services.service_manager import ServiceManager

# 전역 서비스 매니저
service_manager: Optional[ServiceManager] = None


@mcp.tool()
async def fetch_unread_emails(max_results: int = 10) -> dict:
    """
    읽지 않은 이메일을 가져옵니다.
    
    Args:
        max_results: 가져올 최대 이메일 수 (기본값: 10)
    
    Returns:
        dict: {
            "success": bool,
            "emails": [
                {
                    "id": str,
                    "subject": str,
                    "from": str,
                    "snippet": str,
                    "date": str
                }
            ],
            "count": int
        }
    """
    global service_manager
    
    try:
        if not service_manager:
            service_manager = ServiceManager()
            await service_manager.initialize()
        
        emails = await service_manager.gmail.fetch_unread_emails(max_results)
        
        return {
            "success": True,
            "emails": emails,
            "count": len(emails),
            "message": f"{len(emails)}개의 읽지 않은 이메일을 가져왔습니다."
        }
    
    except Exception as e:
        return {
            "success": False,
            "emails": [],
            "count": 0,
            "error": str(e)
        }


@mcp.tool()
async def analyze_email_with_ai(email_content: str, analysis_type: str = "customer_inquiry") -> dict:
    """
    AI로 이메일 내용을 분석합니다.
    
    Args:
        email_content: 분석할 이메일 본문
        analysis_type: 분석 유형 (customer_inquiry, lead_scoring, sentiment)
    
    Returns:
        dict: {
            "success": bool,
            "analysis": {
                "type": str,
                "summary": str,
                "key_points": list,
                "sentiment": str,
                "priority": str,
                "suggested_action": str
            }
        }
    """
    global service_manager
    
    try:
        if not service_manager:
            service_manager = ServiceManager()
            await service_manager.initialize()
        
        analysis = await service_manager.openai.analyze_email(
            email_content, 
            analysis_type
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "message": "이메일 분석이 완료되었습니다."
        }
    
    except Exception as e:
        return {
            "success": False,
            "analysis": None,
            "error": str(e)
        }


@mcp.tool()
async def extract_customer_info(email_content: str) -> dict:
    """
    이메일에서 고객 정보를 추출합니다.
    
    Args:
        email_content: 고객 정보가 포함된 이메일 본문
    
    Returns:
        dict: {
            "success": bool,
            "customer_info": {
                "name": str,
                "email": str,
                "phone": str,
                "company": str,
                "interests": list,
                "budget_range": str
            }
        }
    """
    global service_manager
    
    try:
        if not service_manager:
            service_manager = ServiceManager()
            await service_manager.initialize()
        
        customer_info = await service_manager.openai.extract_customer_info(
            email_content
        )
        
        return {
            "success": True,
            "customer_info": customer_info,
            "message": "고객 정보 추출이 완료되었습니다."
        }
    
    except Exception as e:
        return {
            "success": False,
            "customer_info": None,
            "error": str(e)
        }


@mcp.tool()
async def create_salesforce_lead(customer_data: dict) -> dict:
    """
    Salesforce에 새로운 리드를 생성합니다.
    
    Args:
        customer_data: {
            "first_name": str,
            "last_name": str,
            "email": str,
            "phone": str (optional),
            "company": str,
            "description": str (optional),
            "lead_source": str (기본값: "Email")
        }
    
    Returns:
        dict: {
            "success": bool,
            "lead_id": str,
            "lead_url": str
        }
    """
    global service_manager
    
    try:
        if not service_manager:
            service_manager = ServiceManager()
            await service_manager.initialize()
        
        result = await service_manager.salesforce.create_lead(customer_data)
        
        return {
            "success": True,
            "lead_id": result["id"],
            "lead_url": result["url"],
            "message": f"리드가 생성되었습니다: {result['id']}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "lead_id": None,
            "lead_url": None,
            "error": str(e)
        }


@mcp.tool()
async def search_salesforce_contacts(email: str) -> dict:
    """
    Salesforce에서 연락처를 검색합니다.
    
    Args:
        email: 검색할 이메일 주소
    
    Returns:
        dict: {
            "success": bool,
            "found": bool,
            "contacts": [
                {
                    "id": str,
                    "name": str,
                    "email": str,
                    "account_name": str
                }
            ]
        }
    """
    global service_manager
    
    try:
        if not service_manager:
            service_manager = ServiceManager()
            await service_manager.initialize()
        
        contacts = await service_manager.salesforce.search_contact(email)
        
        return {
            "success": True,
            "found": len(contacts) > 0,
            "contacts": contacts,
            "message": f"{len(contacts)}개의 연락처를 찾았습니다."
        }
    
    except Exception as e:
        return {
            "success": False,
            "found": False,
            "contacts": [],
            "error": str(e)
        }


@mcp.tool()
async def send_email_reply(to: str, subject: str, body: str, thread_id: str = None) -> dict:
    """
    이메일 답장을 보냅니다.
    
    Args:
        to: 수신자 이메일
        subject: 제목
        body: 본문 (HTML 가능)
        thread_id: 답장할 스레드 ID (선택)
    
    Returns:
        dict: {
            "success": bool,
            "message_id": str
        }
    """
    global service_manager
    
    try:
        if not service_manager:
            service_manager = ServiceManager()
            await service_manager.initialize()
        
        message_id = await service_manager.gmail.send_email(
            to=to,
            subject=subject,
            body=body,
            thread_id=thread_id
        )
        
        return {
            "success": True,
            "message_id": message_id,
            "message": "이메일이 성공적으로 전송되었습니다."
        }
    
    except Exception as e:
        return {
            "success": False,
            "message_id": None,
            "error": str(e)
        }


@mcp.tool()
async def process_sales_workflow(email_id: str) -> dict:
    """
    영업 워크플로우를 자동으로 실행합니다:
    1. 이메일 가져오기
    2. AI 분석
    3. 고객 정보 추출
    4. Salesforce 리드 생성
    5. 자동 답장 전송
    
    Args:
        email_id: 처리할 이메일 ID
    
    Returns:
        dict: {
            "success": bool,
            "steps_completed": [str],
            "lead_id": str,
            "reply_sent": bool
        }
    """
    global service_manager
    steps_completed = []
    
    try:
        if not service_manager:
            service_manager = ServiceManager()
            await service_manager.initialize()
        
        # Step 1: 이메일 가져오기
        email = await service_manager.gmail.get_email(email_id)
        steps_completed.append("email_fetched")
        
        # Step 2: AI 분석
        analysis = await service_manager.openai.analyze_email(
            email["body"], 
            "customer_inquiry"
        )
        steps_completed.append("ai_analysis")
        
        # Step 3: 고객 정보 추출
        customer_info = await service_manager.openai.extract_customer_info(
            email["body"]
        )
        steps_completed.append("customer_extracted")
        
        # Step 4: Salesforce 리드 생성
        lead_data = {
            "first_name": customer_info.get("name", "").split()[0],
            "last_name": customer_info.get("name", "").split()[-1] if len(customer_info.get("name", "").split()) > 1 else "Unknown",
            "email": customer_info.get("email", email["from"]),
            "company": customer_info.get("company", "Unknown"),
            "phone": customer_info.get("phone"),
            "description": analysis.get("summary", ""),
            "lead_source": "Email"
        }
        
        lead_result = await service_manager.salesforce.create_lead(lead_data)
        steps_completed.append("lead_created")
        
        # Step 5: 자동 답장
        reply_body = f"""
        안녕하세요 {customer_info.get('name', '고객')}님,
        
        문의해 주셔서 감사합니다. 귀하의 요청을 확인했으며, 
        담당자가 곧 연락드릴 예정입니다.
        
        감사합니다.
        """
        
        await service_manager.gmail.send_email(
            to=email["from"],
            subject=f"Re: {email['subject']}",
            body=reply_body,
            thread_id=email.get("thread_id")
        )
        steps_completed.append("reply_sent")
        
        return {
            "success": True,
            "steps_completed": steps_completed,
            "lead_id": lead_result["id"],
            "reply_sent": True,
            "message": "영업 워크플로우가 성공적으로 완료되었습니다."
        }
    
    except Exception as e:
        return {
            "success": False,
            "steps_completed": steps_completed,
            "lead_id": None,
            "reply_sent": False,
            "error": str(e)
        }


# 서버 실행
if __name__ == "__main__":
    mcp.run()