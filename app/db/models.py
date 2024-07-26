import datetime

from sqlmodel import Field, SQLModel, Relationship


class CollectedTapes(SQLModel, table=True):
    tape_id: str | None = Field(
        default=None,
        foreign_key='tape.id',
        primary_key=True
    )
    profile_address: str | None = Field(
        default=None,
        foreign_key='profile.address',
        primary_key=True
    )
    contract_address: str | None = Field(default=None, primary_key=True)
    asset_id: str | None
    ballance: int = 0

    profile: "Profile" = Relationship(back_populates='collected_tapes')
    tape: "Tape" = Relationship(back_populates='collectors')


class Tape(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)

    name: str | None = None

    score: int | None = None
    title: str | None = None

    buy_value: int = 0
    sell_value: int = 0

    created_at: datetime.datetime | None = None

    creator_address: str | None = Field(
        default=None,
        foreign_key='profile.address'
    )
    creator: "Profile" = Relationship(back_populates="created_tapes")

    rule_id: str | None = Field(default=None, foreign_key='rule.id')
    rule: "Rule" = Relationship(back_populates='tapes')

    collectors: list[CollectedTapes] = Relationship(
        back_populates='tape'
    )

    console_achievements: list["AwardedConsoleAchievement"] = Relationship(
        back_populates='tape'
    )


class CollectedCartridges(SQLModel, table=True):
    cartridge_id: str | None = Field(
        default=None,
        foreign_key='cartridge.id',
        primary_key=True
    )
    profile_address: str | None = Field(
        default=None,
        foreign_key='profile.address',
        primary_key=True
    )
    contract_address: str | None = Field(default=None, primary_key=True)
    asset_id: str | None = Field(default=None, primary_key=True)
    balance: int = 0

    profile: "Profile" = Relationship(back_populates='collected_cartridges')
    cartridge: "Cartridge" = Relationship(back_populates='collectors')


class Cartridge(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)

    name: str
    authors: str | None = None

    created_at: datetime.datetime

    buy_value: int = 0
    sell_value: int = 0

    creator_address: str | None = Field(
        default=None,
        foreign_key='profile.address'
    )
    creator: "Profile" = Relationship(back_populates="created_cartridges")

    collectors: list[CollectedCartridges] = Relationship(
        back_populates='cartridge'
    )
    rules: list["Rule"] = Relationship(back_populates='cartridge')


class Profile(SQLModel, table=True):
    address: str = Field(default=None, primary_key=True)
    points: int = 0

    collected_tapes: list[CollectedTapes] = Relationship(
        back_populates='profile'
    )
    created_tapes: list[Tape] = Relationship(
        back_populates='creator'
    )

    collected_cartridges: list[CollectedCartridges] = Relationship(
        back_populates='profile'
    )
    created_cartridges: list[Cartridge] = Relationship(
        back_populates='creator'
    )

    console_achievements: list["AwardedConsoleAchievement"] = Relationship(
        back_populates='profile'
    )


class Rule(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)

    name: str | None = None
    description: str | None = None
    created_at: datetime.datetime | None = None

    start: datetime.datetime | None = None
    end: datetime.datetime | None = None

    cartridge_id: str | None = Field(default=None, foreign_key='cartridge.id')
    cartridge: Cartridge = Relationship(back_populates='rules')

    created_by: str | None

    tapes: list[Tape] = Relationship(back_populates='rule')


class AwardedConsoleAchievement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    profile_address: str | None = Field(
        default=None,
        foreign_key='profile.address',
    )
    ca_slug: str | None = Field(
        default=None,
        foreign_key='consoleachievement.slug',
    )
    created_at: datetime.datetime | None = None

    points: int = 0
    comments: str | None = None

    profile: Profile = Relationship(back_populates='console_achievements')
    achievement: "ConsoleAchievement" = Relationship(back_populates='awarded')

    tape_id: str | None = Field(
        default=None,
        foreign_key='tape.id',
    )
    tape: Tape = Relationship(back_populates='console_achievements')


class ConsoleAchievement(SQLModel, table=True):
    slug: str = Field(default=None, primary_key=True)

    name: str | None = None
    description: str | None = None

    points: int = 0

    awarded: list[AwardedConsoleAchievement] = Relationship(
        back_populates='achievement'
    )
