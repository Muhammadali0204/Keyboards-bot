from aiogram import Router, F

from .invites_count import router as invites_count_router


router = Router(name="Invite messages")

router.include_routers(
    invites_count_router,
)
