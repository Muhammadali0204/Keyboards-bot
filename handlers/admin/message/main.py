from aiogram import Router

from . import add_message, delete_media_gr, edit_message


router = Router()

router.include_routers(
    add_message.router,
    delete_media_gr.router,
    edit_message.router
)
