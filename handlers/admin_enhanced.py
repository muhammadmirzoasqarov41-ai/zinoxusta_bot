from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup

from config import Config
from db import Database
from keyboards import admin_menu_kb, main_menu_kb
from states import (
    AdminAddDiamonds,
    AdminRemoveDiamonds,
    AdminBroadcast,
    AdminAdBroadcast,
    AdminSendById,
    AdminBlockUser,
    AdminUnblockUser,
    AdminGiveAllDiamonds,
)
from utils import friendly, is_admin
import asyncio
from datetime import datetime, timedelta

router = Router()

# Enhanced admin states
class AdminUserManagement:
    user_search = "admin:user_search"
    user_details = "admin:user_details"
    user_edit = "admin:user_edit"

class AdminAnalytics:
    daily_stats = "admin:daily_stats"
    weekly_stats = "admin:weekly_stats"
    monthly_stats = "admin:monthly_stats"

class AdminContent:
    add_service = "admin:add_service"
    edit_service = "admin:edit_service"
    delete_service = "admin:delete_service"

class AdminNotifications:
    scheduled_message = "admin:scheduled_message"
    custom_broadcast = "admin:custom_broadcast"

# Enhanced admin keyboard
def enhanced_admin_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 User Management", callback_data="admin:users")
    builder.button(text="📊 Analytics Dashboard", callback_data="admin:analytics")
    builder.button(text="💎 Financial Management", callback_data="admin:financial")
    builder.button(text="📝 Content Management", callback_data="admin:content")
    builder.button(text="📢 Notifications", callback_data="admin:notifications")
    builder.button(text="🔧 System Settings", callback_data="admin:settings")
    builder.button(text="🛡️ Security", callback_data="admin:security")
    builder.button(text="📋 Reports", callback_data="admin:reports")
    builder.button(text="⬅️ Back to Main", callback_data="admin:back")
    builder.adjust(2)
    return builder.as_markup()

# User Management Functions
@router.callback_query(lambda c: c.data == "admin:users")
async def admin_users_menu(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Search User", callback_data="admin:user_search")
    builder.button(text="📋 User List", callback_data="admin:user_list")
    builder.button(text="🚫 Blocked Users", callback_data="admin:blocked_users")
    builder.button(text="⭐ Top Users", callback_data="admin:top_users")
    builder.button(text="📈 Active Users", callback_data="admin:active_users")
    builder.button(text="⬅️ Back", callback_data="admin:menu")
    builder.adjust(2)
    
    await callback.message.edit_text(
        friendly("👥 **User Management**\n\nChoose user management option:"),
        reply_markup=builder.as_markup()
    )

@router.callback_query(lambda c: c.data == "admin:user_search")
async def admin_user_search(callback: CallbackQuery, state: FSMContext, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    await state.set_state(AdminUserManagement.user_search)
    await callback.message.edit_text(
        friendly("🔍 **User Search**\n\nEnter user ID, username, or phone number:")
    )

@router.message(AdminUserManagement.user_search)
async def admin_search_user(message: Message, state: FSMContext, db: Database, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        return
    
    search_term = message.text.strip()
    await state.clear()
    
    # Search users by ID, username, or phone
    users = await db.search_users(search_term)
    
    if not users:
        await message.answer(friendly("❌ No users found for: {search_term}"))
        return
    
    builder = InlineKeyboardBuilder()
    for user in users[:10]:  # Limit to 10 results
        user_info = f"{user.get('name', 'Unknown')} (ID: {user.get('tg_id')})"
        builder.button(text=user_info, callback_data=f"admin:user_detail:{user.get('tg_id')}")
    
    builder.button(text="⬅️ Back", callback_data="admin:users")
    builder.adjust(1)
    
    await message.answer(
        friendly(f"📋 **Search Results**\n\nFound {len(users)} users:"),
        reply_markup=builder.as_markup()
    )

@router.callback_query(lambda c: c.data.startswith("admin:user_detail:"))
async def admin_user_detail(callback: CallbackQuery, db: Database, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    user_id = int(callback.data.split(":")[-1])
    user = await db.get_user(user_id)
    
    if not user:
        await callback.answer("❌ User not found")
        return
    
    # Get user statistics
    stats = await db.get_user_stats(user_id)
    
    text = friendly(
        f"👤 **User Details**\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Name: {user.get('name', 'Not set')}\n"
        f"📞 Phone: {user.get('phone', 'Not set')}\n"
        f"📍 Region: {user.get('region', 'Not set')}\n"
        f"💎 Balance: {user.get('diamonds', 0)} 💎\n"
        f"📅 Registered: {user.get('created_at', 'Unknown')}\n"
        f"🚫 Status: {'Blocked' if user.get('is_blocked') else 'Active'}\n\n"
        f"📊 **Statistics:**\n"
        f"🔍 Searches: {stats.get('searches', 0)}\n"
        f"💬 Chats: {stats.get('chats', 0)}\n"
        f"⭐ Reviews: {stats.get('reviews', 0)}\n"
        f"💰 Spent: {stats.get('spent', 0)} 💎"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Add Diamonds", callback_data=f"admin:add_diamonds:{user_id}")
    builder.button(text="➖ Remove Diamonds", callback_data=f"admin:remove_diamonds:{user_id}")
    builder.button(text="📝 Edit Profile", callback_data=f"admin:edit_user:{user_id}")
    builder.button(text="🚫 Block User", callback_data=f"admin:block_user:{user_id}")
    builder.button(text="📊 View Activity", callback_data=f"admin:user_activity:{user_id}")
    builder.button(text("⬅️ Back", callback_data="admin:users"))
    builder.adjust(2)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

# Analytics Dashboard
@router.callback_query(lambda c: c.data == "admin:analytics")
async def admin_analytics_menu(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Daily Stats", callback_data="admin:daily_stats")
    builder.button(text="📆 Weekly Stats", callback_data="admin:weekly_stats")
    builder.button(text="📊 Monthly Stats", callback_data="admin:monthly_stats")
    builder.button(text="📈 Growth Chart", callback_data="admin:growth_chart")
    builder.button(text="💎 Diamond Analytics", callback_data="admin:diamond_analytics")
    builder.button(text="🔥 Popular Services", callback_data="admin:popular_services")
    builder.button(text="📍 Regional Stats", callback_data="admin:regional_stats")
    builder.button(text="⬅️ Back", callback_data="admin:menu")
    builder.adjust(2)
    
    await callback.message.edit_text(
        friendly("📊 **Analytics Dashboard**\n\nChoose analytics option:"),
        reply_markup=builder.as_markup()
    )

@router.callback_query(lambda c: c.data == "admin:daily_stats")
async def admin_daily_stats(callback: CallbackQuery, db: Database, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    # Get daily statistics
    today = datetime.now().date()
    stats = await db.get_daily_stats(today)
    
    text = friendly(
        f"📅 **Daily Statistics - {today}**\n\n"
        f"👥 New Users: {stats.get('new_users', 0)}\n"
        f"🔍 Total Searches: {stats.get('searches', 0)}\n"
        f"💬 Active Chats: {stats.get('active_chats', 0)}\n"
        f"💎 Diamonds Spent: {stats.get('diamonds_spent', 0)}\n"
        f"💰 Revenue: {stats.get('revenue', 0)} 💎\n"
        f"⭐ Reviews Given: {stats.get('reviews', 0)}\n"
        f"🚫 Blocked Users: {stats.get('blocked_users', 0)}\n\n"
        f"📈 **Peak Hours:**\n"
        f"🌅 Morning (6-12): {stats.get('morning_activity', 0)}\n"
        f"☀️ Afternoon (12-18): {stats.get('afternoon_activity', 0)}\n"
        f"🌆 Evening (18-24): {stats.get('evening_activity', 0)}\n"
        f"🌙 Night (0-6): {stats.get('night_activity', 0)}"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 View Chart", callback_data="admin:daily_chart")
    builder.button(text("⬅️ Back", callback_data="admin:analytics"))
    builder.adjust(2)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

# Financial Management
@router.callback_query(lambda c: c.data == "admin:financial")
async def admin_financial_menu(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 Diamond Management", callback_data="admin:diamond_mgmt")
    builder.button(text="💰 Revenue Report", callback_data="admin:revenue")
    builder.button(text="📊 Transaction History", callback_data="admin:transactions")
    builder.button(text="🎁 Bonus Management", callback_data="admin:bonus_mgmt")
    builder.button(text="💳 Payment Settings", callback_data="admin:payment_settings")
    builder.button(text="📈 Financial Forecast", callback_data="admin:forecast")
    builder.button(text="⬅️ Back", callback_data="admin:menu")
    builder.adjust(2)
    
    await callback.message.edit_text(
        friendly("💰 **Financial Management**\n\nChoose financial option:"),
        reply_markup=builder.as_markup()
    )

@router.callback_query(lambda c: c.data == "admin:diamond_mgmt")
async def admin_diamond_management(callback: CallbackQuery, db: Database, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    # Get diamond statistics
    stats = await db.get_diamond_stats()
    
    text = friendly(
        f"💎 **Diamond Management**\n\n"
        f"💰 Total Diamonds in System: {stats.get('total_diamonds', 0)}\n"
        f"👥 Users with Diamonds: {stats.get('users_with_diamonds', 0)}\n"
        f"💸 Diamonds Spent Today: {stats.get('spent_today', 0)}\n"
        f"💸 Diamonds Spent Week: {stats.get('spent_week', 0)}\n"
        f"💸 Diamonds Spent Month: {stats.get('spent_month', 0)}\n"
        f"🎁 Bonus Diamonds Given: {stats.get('bonus_given', 0)}\n"
        f"💵 Average Balance: {stats.get('avg_balance', 0)}\n\n"
        f"📊 **Distribution:**\n"
        f"🥇 Top 10%: {stats.get('top_10_percent', 0)} users\n"
        f"🥈 Top 25%: {stats.get('top_25_percent', 0)} users\n"
        f"🥉 Top 50%: {stats.get('top_50_percent', 0)} users"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Add Diamonds", callback_data="admin:add_diamonds_menu")
    builder.button(text="➖ Remove Diamonds", callback_data="admin:remove_diamonds_menu")
    builder.button(text="🎁 Give Bonus", callback_data="admin:give_bonus")
    builder.button(text="📊 Diamond Report", callback_data="admin:diamond_report")
    builder.button(text("⬅️ Back", callback_data="admin:financial"))
    builder.adjust(2)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

# Content Management
@router.callback_query(lambda c: c.data == "admin:content")
async def admin_content_menu(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔧 Service Categories", callback_data="admin:services")
    builder.button(text="📝 Text Templates", callback_data="admin:templates")
    builder.button(text="🖼️ Media Management", callback_data="admin:media")
    builder.button(text="📋 FAQ Management", callback_data="admin:faq")
    builder.button(text="🎨 Bot Appearance", callback_data="admin:appearance")
    builder.button(text="🌐 Localization", callback_data="admin:localization")
    builder.button(text="⬅️ Back", callback_data="admin:menu")
    builder.adjust(2)
    
    await callback.message.edit_text(
        friendly("📝 **Content Management**\n\nChoose content option:"),
        reply_markup=builder.as_markup()
    )

# Notifications System
@router.callback_query(lambda c: c.data == "admin:notifications")
async def admin_notifications_menu(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📢 Broadcast Message", callback_data="admin:broadcast")
    builder.button(text="🎯 Targeted Message", callback_data="admin:targeted")
    builder.button(text="⏰ Scheduled Message", callback_data="admin:scheduled")
    builder.button(text="📊 Message Stats", callback_data="admin:message_stats")
    builder.button(text="📝 Message Templates", callback_data="admin:msg_templates")
    builder.button(text="⬅️ Back", callback_data="admin:menu")
    builder.adjust(2)
    
    await callback.message.edit_text(
        friendly("📢 **Notification System**\n\nChoose notification option:"),
        reply_markup=builder.as_markup()
    )

# System Settings
@router.callback_query(lambda c: c.data == "admin:settings")
async def admin_settings_menu(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Bot Settings", callback_data="admin:bot_settings")
    builder.button(text="💾 Database Settings", callback_data="admin:db_settings")
    builder.button(text="🔐 Security Settings", callback_data="admin:security_settings")
    builder.button(text="🌐 API Settings", callback_data="admin:api_settings")
    builder.button(text="📊 Performance", callback_data="admin:performance")
    builder.button(text="🔄 Backup & Restore", callback_data="admin:backup")
    builder.button(text="⬅️ Back", callback_data="admin:menu")
    builder.adjust(2)
    
    await callback.message.edit_text(
        friendly("🔧 **System Settings**\n\nChoose settings option:"),
        reply_markup=builder.as_markup()
    )

# Security Tools
@router.callback_query(lambda c: c.data == "admin:security")
async def admin_security_menu(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🚫 User Moderation", callback_data="admin:moderation")
    builder.button(text="🔍 Suspicious Activity", callback_data="admin:suspicious")
    builder.button(text="🛡️ Security Logs", callback_data="admin:security_logs")
    builder.button(text="🚨 Emergency Stop", callback_data="admin:emergency_stop")
    builder.button(text="🔐 Access Control", callback_data="admin:access_control")
    builder.button(text="⬅️ Back", callback_data="admin:menu")
    builder.adjust(2)
    
    await callback.message.edit_text(
        friendly("🛡️ **Security Tools**\n\nChoose security option:"),
        reply_markup=builder.as_markup()
    )

# Reports
@router.callback_query(lambda c: c.data == "admin:reports")
async def admin_reports_menu(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Daily Report", callback_data="admin:daily_report")
    builder.button(text="📆 Weekly Report", callback_data="admin:weekly_report")
    builder.button(text="📈 Monthly Report", callback_data="admin:monthly_report")
    builder.button(text="💰 Financial Report", callback_data="admin:financial_report")
    builder.button(text="👥 User Report", callback_data="admin:user_report")
    builder.button(text="🔧 System Report", callback_data="admin:system_report")
    builder.button(text="⬅️ Back", callback_data="admin:menu")
    builder.adjust(2)
    
    await callback.message.edit_text(
        friendly("📋 **Reports Center**\n\nChoose report type:"),
        reply_markup=builder.as_markup()
    )

# Enhanced admin command
@router.message(Command("admin"))
async def admin_start_enhanced(message: Message, config: Config):
    if not is_admin(message.from_user, config.admin_id, config.admin_username):
        await message.answer(friendly("❌ Access denied. This command is for administrators only."))
        return
    
    await message.answer(
        friendly("🔧 **Enhanced Admin Panel**\n\nWelcome to the comprehensive admin management system."),
        reply_markup=enhanced_admin_menu_kb()
    )

# Back handlers
@router.callback_query(lambda c: c.data == "admin:menu")
async def admin_back_to_menu(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    await callback.message.edit_text(
        friendly("🔧 **Enhanced Admin Panel**\n\nChoose admin option:"),
        reply_markup=enhanced_admin_menu_kb()
    )

@router.callback_query(lambda c: c.data == "admin:back")
async def admin_back_to_main(callback: CallbackQuery, config: Config):
    if not is_admin(callback.from_user, config.admin_id, config.admin_username):
        await callback.answer("❌ Access denied")
        return
    
    await callback.message.edit_text(
        friendly("🏠 **Main Menu**\n\nReturning to main menu."),
        reply_markup=main_menu_kb()
    )
