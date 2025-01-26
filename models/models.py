from tortoise import fields
from tortoise.models import Model
from tortoise.signals import pre_save
from tortoise.exceptions import IntegrityError

from data.config import MAX_CHANNELS_COUNT
from utils.enums import InviteStatus, ButtonStatus, MessageType, InviterBtnType, ChannelType



class User(Model):
    id = fields.BigIntField(pk=True)
    name = fields.TextField()
    
    class Meta:
        table = "users"

    def __str__(self) -> str:
        return self.name


class Invite(Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField('models.User', related_name='inviter', unique=True)
    inviter = fields.ForeignKeyField('models.User', related_name='invites')
    status = fields.CharEnumField(InviteStatus, default=InviteStatus.INVITED)
    
    class Meta:
        table = 'invites'
        unique_together = ('user', 'inviter')
        
    def __str__(self) -> str:
        return self.user.name


class Button(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100)
    parent = fields.ForeignKeyField(
        'models.Button', related_name='childs', null=True
    )
    status = fields.CharEnumField(ButtonStatus, default=ButtonStatus.DEACTIVE)
    
    class Meta:
        table = 'buttons'

    def __str__(self) -> str:
        return self.name


class MessageButton(Model):
    id = fields.IntField(primary_key=True)
    message_type = fields.CharEnumField(MessageType)
    message = fields.JSONField()
    parent_button = fields.ForeignKeyField('models.Button', related_name='messages', null=True)
    media_group_id = fields.BigIntField(null=True)
    status = fields.CharField(max_length=20, default="default")

    class Meta:
        table = 'messages'

    def __str__(self) -> str:
        return self.message_type

    
class InlineButtonMessage(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100)
    url = fields.TextField()
    message = fields.ForeignKeyField('models.MessageButton', related_name='inline_buttons')

    class Meta:
        table = 'inline_buttons'

    def __str__(self) -> str:
        return self.name
    
class InviterButton(Model):
    id = fields.IntField(primary_key=True)
    button = fields.ForeignKeyField('models.Button')
    type = fields.CharEnumField(InviterBtnType, max_length=8)
    limit = fields.IntField(null=True)
    
    class Meta:
        table = 'inviter_button'
        
    @staticmethod
    async def ensure_single(sender, instance, using_db, update_fields):
        if instance.id is None:
            count = await InviterButton.all().count()
            if count >= 1:
                raise IntegrityError('Bu jadvalga faqat bitta ma\'lumot yozish mumkin!')

pre_save(InviterButton)(InviterButton.ensure_single)

class Channel(Model):
    id = fields.IntField(primary_key=True)
    channel_id = fields.BigIntField(unique=True)
    name = fields.CharField(max_length=40)
    url = fields.TextField()
    type = fields.CharEnumField(ChannelType, max_length=8)
    
    class Meta:
        table = 'channels'
        
    @staticmethod
    async def limit_channel(*args, **kwargs):
        count = await Channel.all().count()
        if count >= MAX_CHANNELS_COUNT:
            raise IntegrityError(f'Kanallar maksimal soni {MAX_CHANNELS_COUNT} ta')

pre_save(Channel)(Channel.limit_channel)
