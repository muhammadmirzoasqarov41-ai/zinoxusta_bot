import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from groq import Groq
from config import load_config


@dataclass
class AIMessage:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None


class AIAgent:
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.client = Groq(api_key=api_key)
        self.model = model
        self.conversations: Dict[int, List[AIMessage]] = {}
        
        # System prompt - Usta Top bot uchun maxsus shaxsiyat
        self.system_prompt = """Siz "Usta Top" platformasining aqlli yordamchisidir. 
Sizning vazifangiz:
1. Foydalanuvchilarga usta va xizmatlar topishda yordam berish
2. Texnik masalalar bo'yicha maslahat berish  
3. Ustalar va mijozlar o'rtasida bog'lanish o'rnatish
4. Platforma qoidalarini tushuntirish

Siz har doim do'stona, professional va foydali bo'lishingiz kerak. 
O'zbek tilida javob bering, agar kerak bo'lsa rus tilida ham yordam bering.
Hech qachon shaxsiy ma'lumotlarni so'ramang yoki saqlamang."""

    async def start_conversation(self, user_id: int) -> None:
        """Yangi suhbat boshlash"""
        if user_id not in self.conversations:
            self.conversations[user_id] = [
                AIMessage(role="system", content=self.system_prompt)
            ]

    async def add_message(self, user_id: int, role: str, content: str) -> None:
        """Suhbatga xabar qo'shish"""
        await self.start_conversation(user_id)
        self.conversations[user_id].append(AIMessage(role=role, content=content))
        
        # Oxirgi 20 ta xabarni saqlash (memory limit)
        if len(self.conversations[user_id]) > 20:
            self.conversations[user_id] = self.conversations[user_id][-20:]

    async def get_response(self, user_id: int, user_message: str) -> str:
        """AI dan javob olish"""
        await self.add_message(user_id, "user", user_message)
        
        try:
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in self.conversations[user_id]
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            
            ai_response = response.choices[0].message.content
            await self.add_message(user_id, "assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            return f"AI xizmatida xatolik: {str(e)}. Iltimos, keyinroq urinib ko'ring."

    async def clear_conversation(self, user_id: int) -> None:
        """Suhbatni tozalash"""
        if user_id in self.conversations:
            del self.conversations[user_id]

    async def get_conversation_history(self, user_id: int) -> List[AIMessage]:
        """Suhbat tarixini olish"""
        return self.conversations.get(user_id, [])

    async def is_active_conversation(self, user_id: int) -> bool:
        """Faol suhbat borligini tekshirish"""
        return user_id in self.conversations and len(self.conversations[user_id]) > 1


# Global AI agent instance
ai_agent: Optional[AIAgent] = None


async def get_ai_agent() -> AIAgent:
    """AI agent instance olish"""
    global ai_agent
    if ai_agent is None:
        config = load_config()
        if not config.groq_api_key:
            raise ValueError("Groq API key konfiguratsiyada yo'q")
        ai_agent = AIAgent(config.groq_api_key, config.groq_model)
    return ai_agent


async def init_ai_agent() -> AIAgent:
    """AI agentni ishga tushirish"""
    try:
        return await get_ai_agent()
    except ValueError as e:
        print(f"AI agent ishga tushirilmadi: {e}")
        return None
