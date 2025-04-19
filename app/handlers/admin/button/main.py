from aiogram import Router

from . import edit_button, add_button


router = Router()

router.include_routers(edit_button.router, add_button.router)
