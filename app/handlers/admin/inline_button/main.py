from aiogram import Router

from . import del_inline_btn, add_inline_btn


router = Router()

router.include_routers(
    del_inline_btn.router,
    add_inline_btn.router
)