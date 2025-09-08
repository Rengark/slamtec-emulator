# slamtec_emulator/mock_data.py

import uuid
import time
import random


class RobotState:
    """
    A class to hold the emulated state of the Slamtec robot.
    This acts as our simple in-memory database.
    """

    def __init__(self):
        self.device_id = str(uuid.uuid4()).upper().replace("-", "")

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
            "modelName": "Apollo (Emulated)",
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
            "base.max_moving_speed": 1.0,  # m/s
            "base.max_angular_speed": 2.5,  # rad/s
        }

        # --- SLAM and Motion State ---
        self.pose = {
            "x": 1.0,
            "y": 2.5,
            "z": 0.0,
            "yaw": 1.57,
            "pitch": 0.0,
            "roll": 0.0,
        }

        self.localization_quality = 78

        self.current_action = None
        self.action_history = {}
        self.action_id_counter = 0

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
            },
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
            },
        ]

    def get_new_action_id(self):
        self.action_id_counter += 1
        return self.action_id_counter

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


# Create a single instance of the robot's state to be shared across the app
robot_state = RobotState()
