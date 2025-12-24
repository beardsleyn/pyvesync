"""Data models for VeSync Humidifier devices.

These models inherit from `ResponseBaseModel` and `RequestBaseModel` from the
`base_models` module.

The `InnerHumidifierBaseResult` class is used as a base class for the inner humidifier
result models. The correct subclass is determined by the mashumaro discriminator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Any

from mashumaro.config import BaseConfig
from mashumaro.types import Alias

from pyvesync.models.base_models import (
    ResponseBaseModel,
    ResponseCodeModel,
)


@dataclass
class ResponseHumidifierBase(ResponseCodeModel):
    """Humidifier Base Response Dict."""

    result: OuterHumidifierResult


@dataclass
class OuterHumidifierResult(ResponseBaseModel):
    """Humidifier Result Dict."""

    code: int
    result: InnerHumidifierBaseResult


@dataclass
class InnerHumidifierBaseResult(ResponseBaseModel):
    """Base class for inner humidifier results model.

    All inner results models inherit from this class and are
    correctly subclassed by the mashumaro discriminator.
    """

    class Config(BaseConfig):  # type: ignore[override]
        """Configure the results model to use subclass discriminator."""

        allow_deserialization_not_by_alias = True


class BypassV2InnerErrorResult(InnerHumidifierBaseResult):
    """Inner Error Result Model."""

    msg: str


# Inner Result models for individual devices inherit from InnerHumidifierBaseResult
# and are used to parse the response from the API.
# The correct subclass is determined by the mashumaro discriminator


@dataclass
class ClassicLVHumidResult(InnerHumidifierBaseResult):
    """Classic 200S Humidifier Result Model.

    Inherits from InnerHumidifierBaseResult.
    """

    enabled: bool
    mist_virtual_level: int
    mist_level: int
    mode: str
    display: Annotated[bool, Alias('indicator_light_switch')]
    water_lacks: bool
    humidity: int | None = None
    humidity_high: bool = False
    automatic_stop_reach_target: bool = False
    water_tank_lifted: bool = False
    warm_enabled: bool = False
    warm_level: int | None = None
    night_light_brightness: int | None = None
    configuration: ClassicConfig | None = None


@dataclass
class ClassicConfig(ResponseBaseModel):
    """Classic 200S Humidifier Configuration Model."""

    auto_target_humidity: int = 0
    display: Annotated[bool, Alias('indicator_light_switch')] = False
    automatic_stop: bool = False

    class Config(BaseConfig):  # type: ignore[override]
        """Configure the results model to use subclass discriminator."""

        allow_deserialization_not_by_alias = True
        forbid_extra_keys = False


@dataclass
class LV600SConfig(ResponseBaseModel):
    """LV 600S Humidifier Configuration Model."""

    auto_target_humidity: int = 0
    display: bool = False


@dataclass
class LV600SExtension(ResponseBaseModel):
    """LV 600S Humidifier Configuration Model."""

    timer_remain: int = 0
    schedule_count: int = 0


@dataclass
class LV600SHumidResult(InnerHumidifierBaseResult):
    """LV600S Humidifier Result Model.

    Inherits from InnerHumidifierBaseResult.
    """

    automatic_stop_reach_target: bool
    display: bool
    enabled: bool
    humidity: int
    humidity_high: bool
    mist_level: int
    mist_virtual_level: int
    mode: str
    water_lacks: bool
    water_tank_lifted: bool
    extension: LV600SExtension | None = None
    configuration: LV600SConfig | None = None


# Models for the VeSync Superior 6000S Humidifier


@dataclass
class Superior6000SResult(InnerHumidifierBaseResult):
    """Superior 6000S Humidifier Result Model.

    Inherits from InnerHumidifierBaseResult.
    """

    powerSwitch: int
    humidity: int
    targetHumidity: int
    virtualLevel: int
    mistLevel: int
    workMode: str
    waterLacksState: int
    waterTankLifted: int
    autoStopSwitch: int
    autoStopState: int
    screenSwitch: int
    screenState: int
    scheduleCount: int
    timerRemain: int
    errorCode: int
    autoPreference: int
    childLockSwitch: int
    filterLifePercent: int
    temperature: int
    dryingMode: Superior6000SDryingMode | None = None


@dataclass
class Superior6000SDryingMode(ResponseBaseModel):
    """Drying Mode Model for Superior 6000S Humidifier."""

    dryingLevel: int
    autoDryingSwitch: int
    dryingState: int
    dryingRemain: int


# Models for the Levoit 1000S Humidifier


@dataclass
class Levoit1000SResult(InnerHumidifierBaseResult):
    """Levoit 1000S Humidifier Result Model."""

    powerSwitch: int
    humidity: int
    targetHumidity: int
    virtualLevel: int
    mistLevel: int
    workMode: str
    waterLacksState: int
    waterTankLifted: int
    autoStopSwitch: int
    autoStopState: int
    screenSwitch: int
    screenState: int
    scheduleCount: int
    timerRemain: int
    errorCode: int
    nightLight: Levoit1000SNightLight | None = None


@dataclass
class Levoit1000SNightLight(ResponseBaseModel):
    """Night Light Model for Levoit 1000S Humidifier."""

    nightLightSwitch: int
    brightness: int


@dataclass
class LV600SResult(InnerHumidifierBaseResult):
    """LV600S (LUH-A603S) Humidifier Result Model.

    Uses the newer API format with powerSwitch, workMode, etc.
    Includes warm mist support via warmPower and warmLevel.
    """

    powerSwitch: int
    humidity: int
    targetHumidity: int
    virtualLevel: int
    mistLevel: int
    workMode: str
    waterLacksState: int
    waterTankLifted: int
    autoStopSwitch: int
    autoStopState: int
    screenSwitch: int
    screenState: int
    scheduleCount: int
    timerRemain: int
    errorCode: int
    totalWorkTime: int = 0
    warmPower: bool = False
    warmLevel: int = 0


# Schedule Models for V3 Schedule API


@dataclass
class ScheduleActionParams(ResponseBaseModel):
    """Parameters for a schedule action."""

    mistLevel: int | None = None
    level: int | None = None


@dataclass
class ScheduleAction(ResponseBaseModel):
    """A single action within a schedule.

    Attributes:
        type: Action type ('powerSwitch', 'workMode', 'screenSwitch', 'warm').
        num: Action index (usually 0).
        act: Action value - int for switches (0/1), str for modes ('on'/'off'/'manual').
        params: Optional parameters like mistLevel or warm level.
    """

    type: str
    num: int
    act: int | str
    params: ScheduleActionParams | None = None

    @property
    def act_str(self) -> str:
        """Get action as human-readable string."""
        if isinstance(self.act, int):
            return 'on' if self.act == 1 else 'off'
        return str(self.act)


@dataclass
class ScheduleTimingEvent(ResponseBaseModel):
    """Timing event for a schedule."""

    clkSec: int  # Seconds from midnight


@dataclass
class Schedule(ResponseBaseModel):
    """A humidifier schedule.

    Attributes:
        id: Unique schedule ID.
        enabled: Whether schedule is active.
        type: Schedule type (0 for standard).
        repeat: Day bitmask (0=once, 2=Mon, 4=Tue, 8=Wed, 16=Thu, 32=Fri, 64=Sat, 128=Sun).
        tmgEvt: Timing event with time in seconds from midnight.
        startAct: List of actions to perform.
    """

    id: int
    enabled: bool
    type: int
    repeat: int
    tmgEvt: ScheduleTimingEvent
    startAct: list[ScheduleAction] = field(default_factory=list)

    @property
    def hour(self) -> int:
        """Get hour from clkSec."""
        return self.tmgEvt.clkSec // 3600

    @property
    def minute(self) -> int:
        """Get minute from clkSec."""
        return (self.tmgEvt.clkSec % 3600) // 60

    @property
    def time_str(self) -> str:
        """Get formatted time string HH:MM."""
        return f"{self.hour:02d}:{self.minute:02d}"

    @property
    def days_str(self) -> str:
        """Get human-readable days string."""
        if self.repeat == 0:
            return "once"
        if self.repeat == 254:
            return "daily"
        days = []
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, name in enumerate(day_names):
            if self.repeat & (1 << (i + 1)):
                days.append(name)
        return ','.join(days) if days else "once"

    def _get_action(self, action_type: str) -> ScheduleAction | None:
        """Get action by type."""
        for act in self.startAct:
            if act.type == action_type:
                return act
        return None

    @property
    def power(self) -> str:
        """Get power action as 'on' or 'off'."""
        act = self._get_action('powerSwitch')
        return act.act_str if act else 'unknown'

    @property
    def mode(self) -> str:
        """Get work mode."""
        act = self._get_action('workMode')
        return act.act_str if act else 'unknown'

    @property
    def mist_level(self) -> int | None:
        """Get mist level from workMode action."""
        act = self._get_action('workMode')
        if act and act.params:
            return act.params.mistLevel
        return None

    @property
    def warm(self) -> str:
        """Get warm mist action as 'on' or 'off'."""
        act = self._get_action('warm')
        return act.act_str if act else 'off'

    @property
    def warm_level(self) -> int | None:
        """Get warm mist level."""
        act = self._get_action('warm')
        if act and act.params:
            return act.params.level
        return None

    @property
    def screen(self) -> str:
        """Get screen action as 'on' or 'off'."""
        act = self._get_action('screenSwitch')
        return act.act_str if act else 'unknown'


@dataclass
class SchedulesResult(ResponseBaseModel):
    """Result from getSchedulesV3 API call."""

    total: int
    schedules: list[Schedule] = field(default_factory=list)
