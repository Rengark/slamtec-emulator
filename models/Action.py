from enum import Enum, IntEnum, StrEnum


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
    FAILED = -2
    ABORTED = -1
    DONE = 0
    ONGOING = 1


class SlamtecApiName(StrEnum):
    LOAD_FLOOR = "/api/multi-floor/map/v1/floors/:current"
    CALL_ACTION = "/api/core/motion/v1/actions"
    ABORT_ACTION = "/api/core/motion/v1/actions/:current"
    CHECK_BMS = "/api/core/system/v1/power/status"
    CHECK_POSE = "/api/core/slam/v1/localization/pose"


class SlamtecChangeFloorStatus(IntEnum):
    START = 0
    COMPLETE = 1
    ERROR = -1


class SlamtecChangePoseStatus(IntEnum):
    IDLE = 0
    START = 1
    GOING = 2
