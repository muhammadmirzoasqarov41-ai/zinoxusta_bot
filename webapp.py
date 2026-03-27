from __future__ import annotations

import html

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from aiogram import Bot

from config import Config
from db import Database
from utils import friendly

security = HTTPBasic()


def require_basic(config: Config, creds: HTTPBasicCredentials) -> None:
    if creds.username != config.web_user or creds.password != config.web_pass:
        raise HTTPException(status_code=401, detail="Unauthorized", headers={"WWW-Authenticate": "Basic"})


def build_app(db: Database, config: Config, bot: Bot) -> FastAPI:
    app = FastAPI(title="USTA QIDIR Admin Panel")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request, creds: HTTPBasicCredentials = Depends(security)):
        require_basic(config, creds)
        stats = await db.stats()
        users = await db.list_users(limit=200, offset=0)

        rows = "".join(
            f"<tr>"
            f"<td>{u['id']}</td>"
            f"<td>{u['tg_id']}</td>"
            f"<td>{html.escape(u.get('full_name') or '')}</td>"
            f"<td>{html.escape(u.get('phone') or '')}</td>"
            f"<td>{html.escape(u.get('region') or '')}</td>"
            f"<td>{html.escape(u.get('role') or '')}</td>"
            f"<td>{u.get('diamonds', 0)}</td>"
            f"<td>{'Ha' if u.get('is_blocked') else 'Yo\'q'}</td>"
            f"<td>{u.get('last_seen') or '-'}</td>"
            f"</tr>"
            for u in users
        )

        html_page = f"""
        <html>
        <head>
          <meta charset='utf-8'/>
          <title>USTA QIDIR Admin</title>
          <style>
            body {{ font-family: Arial, sans-serif; margin: 24px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background: #f4f4f4; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
            .card {{ border: 1px solid #ddd; padding: 12px; border-radius: 8px; }}
            .card h3 {{ margin: 0 0 8px 0; }}
            .stats {{ display: flex; gap: 16px; flex-wrap: wrap; }}
            .stat {{ padding: 8px 12px; border: 1px solid #ddd; border-radius: 8px; }}
            form {{ display: flex; flex-direction: column; gap: 6px; }}
            input {{ padding: 6px; }}
            button {{ padding: 8px; cursor: pointer; }}
          </style>
        </head>
        <body>
          <h1>USTA QIDIR Admin Panel</h1>
          <div class='stats'>
            <div class='stat'>Foydalanuvchilar: {stats['total_users']}</div>
            <div class='stat'>Umumiy sarflangan olmos: {stats['total_spent']}</div>
            <div class='stat'>Umumiy balans: {stats['total_balance']}</div>
          </div>

          <h2>Amallar</h2>
          <div class='grid'>
            <div class='card'>
              <h3>Olmos qo'shish</h3>
              <form method='post' action='/add-diamonds'>
                <input name='user_id' placeholder='User ID' required />
                <input name='amount' placeholder='Miqdor' required />
                <button type='submit'>Qo'shish</button>
              </form>
            </div>
            <div class='card'>
              <h3>Olmos ayirish</h3>
              <form method='post' action='/remove-diamonds'>
                <input name='user_id' placeholder='User ID' required />
                <input name='amount' placeholder='Miqdor' required />
                <button type='submit'>Ayirish</button>
              </form>
            </div>
            <div class='card'>
              <h3>Barchaga olmos</h3>
              <form method='post' action='/give-all'>
                <input name='amount' placeholder='Miqdor' required />
                <button type='submit'>Tarqatish</button>
              </form>
            </div>
            <div class='card'>
              <h3>User bloklash</h3>
              <form method='post' action='/block'>
                <input name='user_id' placeholder='User ID' required />
                <button type='submit'>Bloklash</button>
              </form>
            </div>
            <div class='card'>
              <h3>User blokdan olish</h3>
              <form method='post' action='/unblock'>
                <input name='user_id' placeholder='User ID' required />
                <button type='submit'>Blokdan olish</button>
              </form>
            </div>
            <div class='card'>
              <h3>ID orqali xabar</h3>
              <form method='post' action='/send-message'>
                <input name='user_id' placeholder='User ID' required />
                <input name='text' placeholder='Xabar matni' required />
                <button type='submit'>Yuborish</button>
              </form>
            </div>
            <div class='card'>
              <h3>Barcha userlarga xabar</h3>
              <form method='post' action='/broadcast'>
                <input name='text' placeholder='Xabar matni' required />
                <button type='submit'>Yuborish</button>
              </form>
            </div>
          </div>

          <h2>Foydalanuvchilar</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Telegram ID</th>
                <th>Ism</th>
                <th>Telefon</th>
                <th>Hudud</th>
                <th>Rol</th>
                <th>Olmos</th>
                <th>Blok</th>
                <th>So'nggi faollik (UTC)</th>
              </tr>
            </thead>
            <tbody>
              {rows}
            </tbody>
          </table>
        </body>
        </html>
        """
        return HTMLResponse(html_page)

    def _require_auth(creds: HTTPBasicCredentials = Depends(security)) -> None:
        require_basic(config, creds)

    @app.post("/add-diamonds")
    async def add_diamonds(
        user_id: int = Form(...),
        amount: int = Form(...),
        _auth: None = Depends(_require_auth),
    ):
        await db.add_diamonds(user_id, amount)
        try:
            await bot.send_message(
                user_id,
                friendly(
                    f"Tabriklaymiz! Sizning hisobingizga {amount} 💎 Olmos qo'shildi. "
                    "Botimiz sizga doimo xizmat qilishdan mamnun."
                ),
            )
        except Exception:
            pass
        return RedirectResponse("/", status_code=303)

    @app.post("/remove-diamonds")
    async def remove_diamonds(
        user_id: int = Form(...),
        amount: int = Form(...),
        _auth: None = Depends(_require_auth),
    ):
        await db.deduct_diamonds(user_id, amount)
        return RedirectResponse("/", status_code=303)

    @app.post("/give-all")
    async def give_all(amount: int = Form(...), _auth: None = Depends(_require_auth)):
        await db.add_diamonds_all(amount)
        user_ids = await db.list_user_ids()
        for tg_id in user_ids:
            try:
                await bot.send_message(
                    tg_id,
                    friendly(
                        f"Tabriklaymiz! Sizning hisobingizga {amount} 💎 Olmos qo'shildi. "
                        "Bu botimizdan sizga kichik sovg'a."
                    ),
                )
            except Exception:
                pass
        return RedirectResponse("/", status_code=303)

    @app.post("/block")
    async def block(user_id: int = Form(...), _auth: None = Depends(_require_auth)):
        await db.set_blocked(user_id, True)
        return RedirectResponse("/", status_code=303)

    @app.post("/unblock")
    async def unblock(user_id: int = Form(...), _auth: None = Depends(_require_auth)):
        await db.set_blocked(user_id, False)
        return RedirectResponse("/", status_code=303)

    @app.post("/send-message")
    async def send_message(
        user_id: int = Form(...),
        text: str = Form(...),
        _auth: None = Depends(_require_auth),
    ):
        try:
            await bot.send_message(user_id, text)
        except Exception:
            pass
        return RedirectResponse("/", status_code=303)

    @app.post("/broadcast")
    async def broadcast(text: str = Form(...), _auth: None = Depends(_require_auth)):
        user_ids = await db.list_user_ids()
        for tg_id in user_ids:
            try:
                await bot.send_message(tg_id, text)
            except Exception:
                pass
        return RedirectResponse("/", status_code=303)

    return app
