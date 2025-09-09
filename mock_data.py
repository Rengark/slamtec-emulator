# slamtec_emulator/mock_data.py

import uuid
import time
import threading
import math
import random
from models.Pose import Pose3D
from models.Cargo import Cargo
from models.Action import ActionInfo, ActionState


class RobotState:
    """
    A class to hold the emulated state of the Slamtec robot.
    This acts as our simple in-memory database.
    """

    def __init__(self):
        self.device_id = "DE55F0684397409280D8625264CD921B"  # str(uuid.uuid4()).upper().replace("-", "")

        # --- System State ---
        self.power_status = {
            "batteryPercentage": 95,
            "isCharging": False,
            "isDCConnected": False,
            "dockingStatus": "not_on_dock",
            "powerStage": "running",
            "sleepMode": "awake",
        }

        self.robot_info = {
            "manufacturerId": 255,
            "manufacturerName": "Slamtec (Emulated)",
            "modelId": 43792,
            "modelName": "H2 (Emulated)",
            "deviceID": self.device_id,
            "hardwareVersion": "1.0.0",
            "softwareVersion": "1.1.0-emulated",
        }

        self.robot_health = {
            "hasWarning": False,
            "hasError": False,
            "hasFatal": False,
            "baseError": [],
        }

        self.system_params = {
            "base.max_moving_speed": 1.2,  # m/s
            "base.max_angular_speed": 2.5,  # rad/s
        }

        # --- SLAM and Motion State ---
        self.pose = Pose3D(x=1.0, y=2.5, z=0.0, yaw=1.57, pitch=0.0, roll=0.0)

        self.localization_quality = 78

        self.current_action = ActionInfo()
        self.action_history = {}
        self.action_id_counter = -1

        # --- Artifacts State ---
        self.pois = {
            str(uuid.uuid4()): {
                "id": "e8d7f6c8-a1b2-c3d4-e5f6-a7b8c9d0e1f2",
                "pose": {"x": 5.0, "y": 3.0, "yaw": 0.0},
                "metadata": {"display_name": "Charging Station"},
            },
            str(uuid.uuid4()): {
                "id": "b1c2d3e4-f5a6-b7c8-d9e0-f1a2b3c4d5e6",
                "pose": {"x": -2.0, "y": 4.5, "yaw": 3.14},
                "metadata": {"display_name": "yes"},
            },
        }
        self.virtual_walls = {}
        self.virtual_tracks = {}

        self.cargos = [
            Cargo.from_dict(
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "pos": 0,
                    "orientation": "FRONT",
                    "layer": 0,
                    "type": "TAKEOUT",
                    "errors": [],
                    "boxes": [
                        {
                            "id": 0,
                            "door_status": "CLOSED",
                            "lock_status": "LOCKED",
                            "stock_status": "EMPTY",
                            "status": "EMPTY",
                            "errors": [],
                        }
                    ],
                }
            ),
            Cargo.from_dict(
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                    "pos": 0,
                    "orientation": "FRONT",
                    "layer": 0,
                    "type": "TAKEOUT",
                    "errors": [],
                    "boxes": [
                        {
                            "id": 0,
                            "door_status": "CLOSED",
                            "lock_status": "LOCKED",
                            "stock_status": "EMPTY",
                            "status": "EMPTY",
                            "errors": [],
                        }
                    ],
                }
            ),
        ]
        self._action_lock = threading.Lock()  # To prevent race conditions with actions
        self.action_cancel_event = None

    def get_new_action_id(self):
        self.action_id_counter += 1
        return self.action_id_counter

    def start_new_action(self, action_name, options):
        """Creates and starts a new action, running the simulation in a background thread."""
        with self._action_lock:
            if self.current_action:
                # A real robot might queue actions, but for this emulator,
                # we'll only allow one at a time.
                return None  # Indicate failure to create action

            action_id = self.get_new_action_id()

            # This is the ActionInfo object that gets returned immediately
            self.current_action = {
                "action_id": action_id,
                "action_name": action_name,
                "stage": "New",
                "state": {
                    "status": 0,  # 0: NewBorn, 1: Working, 4: Done
                    "result": 0,  # 0: Success
                    "reason": "",
                },
            }
            self.action_cancel_event = threading.Event()
            # Start the appropriate simulation in the background
            # Here we only simulate 'MoveToAction' as an example
            if action_name == "slamtec.agent.actions.MoveToAction":
                thread = threading.Thread(
                    target=self._simulate_move_to_action,
                    args=(action_id, options, self.action_cancel_event),
                )
                thread.start()
            else:
                # For other actions, we can just mark them as instantly complete
                print(
                    f"Warning: Action '{action_name}' is not simulated. Completing immediately."
                )
                self.current_action["state"]["status"] = 4  # Done
                self.action_history[action_id] = self.current_action
                self.current_action = None

            return self.action_history.get(action_id) or self.current_action

    def _simulate_move_to_action(self, action_id, options, cancel_event):
        """The background worker function that simulates robot movement."""
        print(f"[Action {action_id}] Started: Moving to {options.get('target')}")

        # --- Update action state to 'Working' ---
        with self._action_lock:
            self.current_action["stage"] = "MOVING_TO_TARGET"
            self.current_action["state"]["status"] = 1  # Working

        target = options.get("target", {})
        target_x = target.get("x", self.pose["x"])
        target_y = target.get("y", self.pose["y"])

        # --- Simple simulation logic ---
        start_x, start_y = self.pose["x"], self.pose["y"]
        distance = math.sqrt((target_x - start_x) ** 2 + (target_y - start_y) ** 2)

        speed = 0.5  # meters per second
        duration = distance / speed
        steps = int(duration * 10)  # 10 steps per second

        if steps == 0:
            steps = 1

        for i in range(steps):
            # check for cancel action signal
            if cancel_event.is_set():
                print(
                    f"[Action {action_id}] Received abort signal. Stopping simulation."
                )
                return  # Exit the thread
            time.sleep(0.1)
            progress = (i + 1) / steps
            # Linearly interpolate the position
            with self._action_lock:
                self.pose["x"] = start_x + (target_x - start_x) * progress
                self.pose["y"] = start_y + (target_y - start_y) * progress
                # print(f"[Action {action_id}] Progress: {int(progress*100)}%, Pose: ({self.pose['x']:.2f}, {self.pose['y']:.2f})")

        # --- Finalize the action ---
        with self._action_lock:
            if cancel_event.is_set():
                return
            self.pose["x"] = target_x
            self.pose["y"] = target_y
            self.current_action["stage"] = "Arrived"
            self.current_action["state"]["status"] = 4  # Done
            self.current_action["state"]["result"] = 0  # Success

            # Move from current to history
            self.action_history[action_id] = self.current_action
            self.current_action = None
            print(
                f"[Action {action_id}] Finished. Final pose: ({self.pose['x']:.2f}, {self.pose['y']:.2f})"
            )

    def abort_current_action(self):
        """Aborts the currently running action."""
        with self._action_lock:
            if not self.current_action:
                return False  # No action to abort

            action_id = self.current_action["action_id"]
            print(f"[Action {action_id}] Aborting action...")

            # 1. Signal the background thread to stop
            if self.action_cancel_event:
                self.action_cancel_event.set()

            # 2. Update the state as requested
            self.current_action["state"]["status"] = 4  # Done
            self.current_action["state"]["result"] = -2  # Aborted
            self.current_action["state"]["reason"] = "Aborted by user"
            self.current_action["stage"] = "Aborted"

            # 3. Move it to the history
            self.action_history[action_id] = self.current_action

            # 4. Clear the current action
            self.current_action = None
            self.action_cancel_event = None

            print(f"[Action {action_id}] Moved to history with 'Aborted' status.")
            return True

    def update_pose(self, new_pose):
        self.pose.update(new_pose)

    def add_poi(self, poi_data):
        # In a real scenario, we'd validate the schema
        poi_id = poi_data.get("id", str(uuid.uuid4()))
        if "pose" not in poi_data:
            # If no pose provided, use the robot's current pose
            poi_data["pose"] = {
                "x": self.pose["x"],
                "y": self.pose["y"],
                "yaw": self.pose["yaw"],
            }
        self.pois[poi_id] = poi_data
        return poi_data

    def delete_poi(self, poi_id):
        if poi_id in self.pois:
            del self.pois[poi_id]
            return True
        return False

    def handle_door_operation(self, operation: str, cargo_id: str, box_id: int = 0):
        for cargo in self.cargos:
            if cargo.id == cargo_id:
                for box in cargo.boxes:
                    if box.id == box_id:
                        cargo.operation(operation)
                        return


# Create a single instance of the robot's state to be shared across the app
robot_state = RobotState()
