from enum import Enum

from aiogram.types import (
    InputMediaAnimation,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
)


class MessageType(str, Enum):
    TEXT = "text"
    PHOTO = "photo"
    DOCUMENT = "document"
    VIDEO = "video"
    ANIMATION = "animation"
    AUDIO = "audio"
    STICKER = "sticker"
    LOCATION = "location"


class InviteStatus(str, Enum):
    INVITED = "invited"
    INVITE_DONE = "invite_done"
    INVITE_EXPIRED = "invite_expired"


class ButtonStatus(str, Enum):
    ACTIVE = "active"
    DEACTIVE = "deactive"
    TOP_ACTIVE = "top_active"


class InviterBtnType(str, Enum):
    LIMITED = "limited"
    RATING = "rating"


class ChannelType(str, Enum):
    DEFAULT = "default"
    GIFT = "gift"


MEDIA_CLASSES = {
    MessageType.PHOTO: InputMediaPhoto,
    MessageType.ANIMATION: InputMediaAnimation,
    MessageType.AUDIO: InputMediaAudio,
    MessageType.DOCUMENT: InputMediaDocument,
    MessageType.VIDEO: InputMediaVideo,
}

MEDALS = ["🏆", "🥈", "🥉", "🏅", "🏅"]
