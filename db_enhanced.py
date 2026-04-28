"""Enhanced database functions for admin panel"""
import aiosqlite
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

class EnhancedDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    async def search_users(self, search_term: str) -> List[Dict]:
        """Search users by ID, username, or phone"""
        async with aiosqlite.connect(self.db_path) as db:
            if search_term.isdigit():
                # Search by ID
                await db.execute(
                    "SELECT * FROM users WHERE tg_id = ?",
                    (int(search_term),)
                )
            else:
                # Search by username or phone
                await db.execute(
                    "SELECT * FROM users WHERE name LIKE ? OR phone LIKE ?",
                    (f"%{search_term}%", f"%{search_term}%")
                )
            rows = await db.fetchall()
            return [dict(row) for row in rows]
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get comprehensive user statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get user searches
            await db.execute(
                "SELECT COUNT(*) as searches FROM search_history WHERE user_id = ?",
                (user_id,)
            )
            searches = (await db.fetchone())['searches']
            
            # Get user chats
            await db.execute(
                "SELECT COUNT(*) as chats FROM chat_history WHERE user_id = ?",
                (user_id,)
            )
            chats = (await db.fetchone())['chats']
            
            # Get user reviews
            await db.execute(
                "SELECT COUNT(*) as reviews FROM reviews WHERE user_id = ?",
                (user_id,)
            )
            reviews = (await db.fetchone())['reviews']
            
            # Get user spent diamonds
            await db.execute(
                "SELECT COALESCE(SUM(amount), 0) as spent FROM diamond_transactions WHERE user_id = ? AND amount < 0",
                (user_id,)
            )
            spent = abs((await db.fetchone())['spent'])
            
            return {
                'searches': searches,
                'chats': chats,
                'reviews': reviews,
                'spent': spent
            }
    
    async def get_daily_stats(self, date: datetime.date) -> Dict:
        """Get daily statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # New users
            await db.execute(
                "SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = ?",
                (date,)
            )
            new_users = (await db.fetchone())['count']
            
            # Searches
            await db.execute(
                "SELECT COUNT(*) as count FROM search_history WHERE DATE(created_at) = ?",
                (date,)
            )
            searches = (await db.fetchone())['count']
            
            # Active chats
            await db.execute(
                "SELECT COUNT(*) as count FROM chat_history WHERE DATE(created_at) = ?",
                (date,)
            )
            active_chats = (await db.fetchone())['count']
            
            # Diamonds spent
            await db.execute(
                "SELECT COALESCE(SUM(amount), 0) as spent FROM diamond_transactions WHERE DATE(created_at) = ? AND amount < 0",
                (date,)
            )
            diamonds_spent = abs((await db.fetchone())['spent'])
            
            # Revenue
            await db.execute(
                "SELECT COALESCE(SUM(amount), 0) as revenue FROM diamond_transactions WHERE DATE(created_at) = ? AND amount < 0",
                (date,)
            )
            revenue = abs((await db.fetchone())['revenue'])
            
            # Reviews
            await db.execute(
                "SELECT COUNT(*) as count FROM reviews WHERE DATE(created_at) = ?",
                (date,)
            )
            reviews = (await db.fetchone())['count']
            
            # Blocked users
            await db.execute(
                "SELECT COUNT(*) as count FROM users WHERE is_blocked = 1 AND DATE(updated_at) = ?",
                (date,)
            )
            blocked_users = (await db.fetchone())['count']
            
            # Peak hours
            morning = await self._get_activity_by_hour(date, 6, 12)
            afternoon = await self._get_activity_by_hour(date, 12, 18)
            evening = await self._get_activity_by_hour(date, 18, 24)
            night = await self._get_activity_by_hour(date, 0, 6)
            
            return {
                'new_users': new_users,
                'searches': searches,
                'active_chats': active_chats,
                'diamonds_spent': diamonds_spent,
                'revenue': revenue,
                'reviews': reviews,
                'blocked_users': blocked_users,
                'morning_activity': morning,
                'afternoon_activity': afternoon,
                'evening_activity': evening,
                'night_activity': night
            }
    
    async def _get_activity_by_hour(self, date: datetime.date, start_hour: int, end_hour: int) -> int:
        """Get activity count for specific hour range"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                SELECT COUNT(*) as count FROM (
                    SELECT user_id FROM search_history WHERE DATE(created_at) = ? AND strftime('%H', created_at) >= ? AND strftime('%H', created_at) < ?
                    UNION
                    SELECT user_id FROM chat_history WHERE DATE(created_at) = ? AND strftime('%H', created_at) >= ? AND strftime('%H', created_at) < ?
                )
                """,
                (date, str(start_hour), str(end_hour), date, str(start_hour), str(end_hour))
            )
            return (await db.fetchone())['count']
    
    async def get_diamond_stats(self) -> Dict:
        """Get comprehensive diamond statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total diamonds in system
            await db.execute(
                "SELECT COALESCE(SUM(diamonds), 0) as total FROM users"
            )
            total_diamonds = (await db.fetchone())['total']
            
            # Users with diamonds
            await db.execute(
                "SELECT COUNT(*) as count FROM users WHERE diamonds > 0"
            )
            users_with_diamonds = (await db.fetchone())['count']
            
            # Diamonds spent today
            today = datetime.now().date()
            await db.execute(
                "SELECT COALESCE(SUM(amount), 0) as spent FROM diamond_transactions WHERE DATE(created_at) = ? AND amount < 0",
                (today,)
            )
            spent_today = abs((await db.fetchone())['spent'])
            
            # Diamonds spent this week
            week_ago = datetime.now() - timedelta(days=7)
            await db.execute(
                "SELECT COALESCE(SUM(amount), 0) as spent FROM diamond_transactions WHERE created_at >= ? AND amount < 0",
                (week_ago,)
            )
            spent_week = abs((await db.fetchone())['spent'])
            
            # Diamonds spent this month
            month_ago = datetime.now() - timedelta(days=30)
            await db.execute(
                "SELECT COALESCE(SUM(amount), 0) as spent FROM diamond_transactions WHERE created_at >= ? AND amount < 0",
                (month_ago,)
            )
            spent_month = abs((await db.fetchone())['spent'])
            
            # Bonus diamonds given
            await db.execute(
                "SELECT COALESCE(SUM(amount), 0) as bonus FROM diamond_transactions WHERE amount > 0",
            )
            bonus_given = (await db.fetchone())['bonus']
            
            # Average balance
            await db.execute(
                "SELECT COALESCE(AVG(diamonds), 0) as avg FROM users"
            )
            avg_balance = (await db.fetchone())['avg']
            
            # Distribution
            total_users = await self._get_total_users()
            top_10 = await self._get_users_with_diamonds_above(total_diamonds * 0.9)
            top_25 = await self._get_users_with_diamonds_above(total_diamonds * 0.75)
            top_50 = await self._get_users_with_diamonds_above(total_diamonds * 0.5)
            
            return {
                'total_diamonds': total_diamonds,
                'users_with_diamonds': users_with_diamonds,
                'spent_today': spent_today,
                'spent_week': spent_week,
                'spent_month': spent_month,
                'bonus_given': bonus_given,
                'avg_balance': avg_balance,
                'top_10_percent': top_10,
                'top_25_percent': top_25,
                'top_50_percent': top_50
            }
    
    async def _get_total_users(self) -> int:
        """Get total number of users"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("SELECT COUNT(*) as count FROM users")
            return (await db.fetchone())['count']
    
    async def _get_users_with_diamonds_above(self, threshold: float) -> int:
        """Get number of users with diamonds above threshold"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "SELECT COUNT(*) as count FROM users WHERE diamonds > ?",
                (threshold,)
            )
            return (await db.fetchone())['count']
