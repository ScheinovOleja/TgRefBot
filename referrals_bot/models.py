from pony.orm import Database, PrimaryKey, Optional, Required, Set

from referrals_bot import config

db = Database()
db.bind(**config['DATABASE'], provider='postgres')


class AllUsers(db.Entity):
    id = PrimaryKey(int, auto=True)
    tg_id = Required(str, unique=True)
    subscribe_user = Optional('SubscribeUsers', reverse='user', index=True)
    referral_user = Set('InvitedUser', reverse='referrals', index=True)
    who_invited = Optional('InvitedUser', reverse='user')
    member_airdrop = Optional('MembersAirdrop', reverse='user')

    @classmethod
    def get_or_create(cls, **kwargs):
        r = cls.get(**kwargs)
        if r is None:
            return cls(**kwargs), True
        else:
            return r, False


class SubscribeUsers(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Optional(AllUsers, nullable=True, reverse='subscribe_user', column='user_id', cascade_delete=False)

    @classmethod
    def get_or_create(cls, **kwargs):
        r = cls.get(**kwargs)
        if r is None:
            return cls(**kwargs), True
        else:
            return r, False


class InvitedUser(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Optional(AllUsers, nullable=True, reverse='who_invited', column='user_id', cascade_delete=False)
    referrals = Optional(AllUsers, nullable=True, column='who_invite_id', reverse='referral_user', cascade_delete=False)

    @classmethod
    def get_or_create(cls, **kwargs):
        r = cls.get(**kwargs)
        if r is None:
            return cls(**kwargs), True
        else:
            return r, False


class MembersAirdrop(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Optional(AllUsers, nullable=True, reverse='member_airdrop', column='user_id', cascade_delete=False)


class Groups(db.Entity):
    id = PrimaryKey(int, auto=True)
    link_group = Required(str)
    id_group = Required(str)
    name_group = Required(str)


db.generate_mapping(create_tables=True)
