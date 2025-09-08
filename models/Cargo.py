import uuid
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

OPERATION_TIMER = 3.0

# --- Enumerations for Status Fields ---
# Using Enums makes the code safer and more readable than using plain strings.


class DoorStatus(Enum):
    OPEN = "OPEN"
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"
    SEMIOPEN = "SEMIOPEN"


class LockStatus(Enum):
    LOCKED = "LOCKED"
    UNLOCKED = "UNLOCKED"


class StockStatus(Enum):
    EMPTY = "EMPTY"
    SEMIFULL = "SEMIFULL"
    FULL = "FULL"


class BoxStatus(Enum):
    EMPTY = "EMPTY"
    NOT_EMPTY = "NOT_EMPTY"
    ERROR = "ERROR"


class CargoOrientation(Enum):
    FRONT = "FRONT"
    BACK = "BACK"
    TOP = "TOP"


class CargoType(Enum):
    TAKEOUT = "TAKEOUT"
    RETAIL = "RETAIL"


# --- Box Class ---


@dataclass
class Box:
    """Represents a single box within a cargo bay."""

    id: int = 0
    door_status: DoorStatus = DoorStatus.CLOSED.value
    lock_status: LockStatus = LockStatus.LOCKED.value
    stock_status: StockStatus = StockStatus.EMPTY.value
    status: BoxStatus = BoxStatus.EMPTY
    errors: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Box":
        """Creates a Box instance from a dictionary."""
        return cls(
            id=data["id"],
            door_status=DoorStatus(data["door_status"]),
            lock_status=LockStatus(data["lock_status"]),
            stock_status=StockStatus(data["stock_status"]),
            status=BoxStatus(data["status"]),
            errors=data.get("errors", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Box instance to a dictionary."""
        return {
            "id": self.id,
            "doorStatus": self.door_status.value,
            "lockStatus": self.lock_status.value,
            "stockStatus": self.stock_status.value,
            "status": self.status.value,
            "errors": self.errors,
        }


# --- Cargo Class ---


@dataclass
class Cargo:
    """Represents a cargo bay, which contains multiple boxes."""

    id: str
    pos: int
    orientation: CargoOrientation
    layer: int
    type: CargoType
    errors: List[str] = field(default_factory=list)
    boxes: List[Box] = field(default_factory=list)

    # hidden variables for emulating the behavior
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _active_thread: Optional[threading.Thread] = field(default=None, repr=False)
    _cancel_event: Optional[threading.Event] = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cargo":
        """Creates a Cargo instance from a dictionary, including nested Boxes."""
        # Convert the list of box dictionaries into a list of Box objects
        box_objects = [Box.from_dict(box_data) for box_data in data.get("boxes", [])]

        return cls(
            id=data["id"],
            pos=data["pos"],
            orientation=CargoOrientation(data["orientation"]),
            layer=data["layer"],
            type=CargoType(data["type"]),
            errors=data.get("errors", []),
            boxes=box_objects,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Cargo instance to a dictionary, including nested Boxes."""
        return {
            "id": self.id,
            "pos": self.pos,
            "orientation": self.orientation.value,
            "layer": self.layer,
            "type": self.type.value,
            "errors": self.errors,
            # Convert the list of Box objects back into a list of dictionaries
            "boxes": [box.to_dict() for box in self.boxes],
        }

    def operation(self, door_action: DoorStatus, box: int):
        if door_action not in (DoorStatus.OPEN, DoorStatus.CLOSED):
            print(f"Bad door action encouentered: {door_action}")
            return

        with self._lock:
            # --- 1. Cancel any existing operation ---
            if self._active_thread and self._active_thread.is_alive():
                print(f"Box {self.id}: Cancelling previous operation...")
                self._cancel_event.set()  # Signal the old thread to stop
                self._active_thread.join(timeout=1.0)  # Wait briefly for it to exit

            # --- 2. Set the initial state ---
            if door_action == DoorStatus.OPEN:
                if self.boxes[box].door_status in [DoorStatus.OPEN, DoorStatus.OPENING]:
                    print(f"Box {self.id}: Already open or opening. No action taken.")
                    return
                self.boxes[box].door_status = DoorStatus.OPENING
            elif door_action == DoorStatus.CLOSED:
                if self.boxes[box].door_status in [
                    DoorStatus.CLOSED,
                    DoorStatus.CLOSING,
                ]:
                    print(f"Box {self.id}: Already closed or closing. No action taken.")
                    return
                self.boxes[box].door_status = DoorStatus.CLOSING

            # --- 3. Start the new operation in a background thread ---
            self._cancel_event = threading.Event()

            # The worker function now needs the cancel event
            def _delayed_action(cancel_event: threading.Event):
                print(
                    f"Box {self.id}: Starting {OPERATION_TIMER}s operation to set status to {door_action.value}..."
                )

                # Instead of time.sleep(), we wait on the event.
                # It returns False if it times out (completes), True if set (cancelled).
                was_cancelled = cancel_event.wait(timeout=OPERATION_TIMER)

                # The 'with self._lock' ensures we don't change the state
                # while another command is trying to cancel us.
                with self._lock:
                    if was_cancelled:
                        print(f"Box {self.id}: Operation was cancelled.")
                    else:
                        self.boxes[box].door_status = door_action
                        print(
                            f"Box {self.id}: Status updated to {self.boxes[box].door_status.value}."
                        )

                    # Clear the active thread since this one is now finished
                    self._active_thread = None
                    self._cancel_event = None

            self._active_thread = threading.Thread(
                target=_delayed_action, args=(self._cancel_event,)
            )
            self._active_thread.start()
