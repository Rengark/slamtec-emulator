from enum import Enum, IntEnum, StrEnum
from dataclasses import dataclass, field


class SlamtecActionName(StrEnum):  # Only used when SlamtecApiName is CALL_ACTION
    # Known actions to be used for now
    MOVE_TO = "slamtec.agent.actions.MoveToAction"
    GO_HOME = "slamtec.agent.actions.GoHomeAction"
    RECOVER_LOCALISATION = "slamtec.agent.actions.RecoverLocalizationAction"
    LEAVE_ELEVATOR = "slamtec.agent.actions.LeaveElevatorAction"
    ENTER_ELEVATOR = "slamtec.agent.actions.EnterElevatorAction"

    # Uknown/ unused actions for now
    MANUAL_RELOCALISATION = "slamtec.agent.actions.ManualRelocalizationAction"
    DELIVERY_TASK_LIST = "slamtec.agent.actions.DeliveryTaskListAction"
    DELIVERY_TASK_ACTION = "slamtec.agent.actions.DeliveryTaskAction"
    RETURN_PARKING_ACTION = "slamtec.agent.actions.ReturnToParkingAction"
    HEALTH_SUPERVISORY = "slamtec.agent.actions.HealthSupervisoryAction"
    MULTI_FLOOR_BACK_HOME = "slamtec.agent.actions.MultiFloorBackHomeAction"
    MULTI_FLOOR_MOVE = "slamtec.agent.actions.MultiFloorMoveAction"
    TRANSFER_ELEVATOR = "slamtec.agent.actions.TransferElevatorAction"
    SWEEP = "slamtec.agent.actions.SweepAction"
    BACK_OFF_FROM_TAG = "slamtec.agent.actions.BackOffFromTagAction"
    ROTATE_TO = "slamtec.agent.actions.RotateToAction"
    ROTATE = "slamtec.agent.actions.RotateAction"
    MOVE_BY = "slamtec.agent.actions.MoveByAction"
    MOVE_TO_TAG = "slamtec.agent.actions.MoveToTagAction"
    SERIES_MOVE_TO = "slamtec.agent.actions.SeriesMoveToAction"
    NONE = "NONE"


class SlamtecActionStatus(IntEnum):
    NEWBORN = 0
    WORKING = 1
    PAUSED = 2
    DONE = 4


class SlamtecActionResult(IntEnum):
    SUCCESS = 0
    FAILED = -1
    ABORTED = -2


@dataclass
class ActionState:
    status: SlamtecActionStatus = SlamtecActionStatus.NEWBORN
    result: SlamtecActionResult = SlamtecActionResult.SUCCESS
    reason: str = str()


@dataclass
class ActionInfo:
    action_id: int = -1
    action_name: SlamtecActionName = SlamtecActionName.NONE
    stage: str = str()
    state: ActionState = field(default_factory=ActionState)
