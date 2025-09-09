# slamtec_emulator/app.py

import json
import re
from flask import Flask, jsonify, request, Response
from mock_data import robot_state
from models.Cargo import DoorStatus
# --- Utility Functions ---


def convert_path_to_flask(path):
    """Converts OpenAPI path format {param} to Flask's <type:param>."""
    return re.sub(r"{(\w+)}", r"<string:\1>", path)


# --- Flask App Initialization ---

app = Flask(__name__)

# --- Mock API Logic Functions ---


def get_power_status():
    """Handler for GET /api/core/system/v1/power/status"""
    return jsonify(robot_state.power_status)


def get_robot_info():
    """Handler for GET /api/core/system/v1/robot/info"""
    return jsonify(robot_state.robot_info)


def get_robot_health():
    """Handler for GET /api/core/system/v1/robot/health"""
    return jsonify(robot_state.robot_health)


def shutdown_robot():
    """Handler for POST /api/core/system/v1/power/:shutdown"""
    data = request.get_json()
    shutdown_time = data.get("shutdown_time_interval", 0)
    restart_time = data.get("restart_time_interval", 0)

    print(
        f"Received shutdown request: shutdown in {shutdown_time} mins, restart in {restart_time} mins."
    )
    # Here you could simulate a state change
    robot_state.power_status["powerStage"] = "shutingdown"
    return jsonify(True)


def get_pose():
    """Handler for GET /api/core/slam/v1/localization/pose"""
    return jsonify(robot_state.pose)


def set_pose():
    """Handler for PUT /api/core/slam/v1/localization/pose"""
    new_pose_data = request.get_json()
    robot_state.update_pose(new_pose_data)
    print(f"Robot pose updated to: {robot_state.pose}")
    return jsonify({"status": "success", "pose": robot_state.pose})


def get_current_pois():
    """Handler for GET /api/core/artifact/v1/pois"""
    return jsonify(list(robot_state.pois.values()))


def add_poi():
    """Handler for POST /api/core/artifact/v1/pois"""
    poi_data = request.get_json()
    new_poi = robot_state.add_poi(poi_data)
    print(f"Added new POI: {new_poi}")
    return jsonify(new_poi), 201


def delete_poi(poi_id):
    """Handler for DELETE /api/core/artifact/v1/pois/{poi_id}"""
    if robot_state.delete_poi(poi_id):
        print(f"Deleted POI with ID: {poi_id}")
        return jsonify(True)
    else:
        return jsonify({"error": "POI not found"}), 404


@app.route(
    "/api/delivery/v1/cargos/<string:cargo_id>/boxes/<int:box_id>/<string:operation>",
    methods=["PUT"],
)
def operate_box(cargo_id, box_id, operation):
    """
    Triggers a box to open or close, interrupting any prior command.
    """
    target_status = None
    if operation.lower() == ":open":
        target_status = DoorStatus.OPEN
    elif operation.lower() == ":close":
        target_status = DoorStatus.CLOSED
    else:
        return jsonify({"error": "Invalid operation. Use 'open' or 'close'."}), 400

    # (Find the box_to_operate as before...)
    box_to_operate = None

    for cargo in robot_state.cargos:
        if cargo.id == cargo_id:
            box_to_operate = cargo
            cargo.operation(target_status, box_id)
            break

    if not box_to_operate:
        return jsonify({"error": f"Box with ID {box_id} not found."}), 404

    # The call is now much simpler and safer
    # box_to_operate.operation(target_status, box_id)

    return jsonify(
        {
            "message": f"Command '{operation}' sent to Box {box_id}. Current status: {box_to_operate.boxes[box_id].door_status.value}"
        }
    )


def create_action(payload):
    """Handler for POST /api/core/motion/v1/actions"""
    data = request.get_json()
    if not data or "action_name" not in data:
        return jsonify({"error": "action_name is required"}), 400

    action_name = data.get("action_name")
    options = data.get("options", {})

    # Try to start the new action
    action_info = robot_state.start_new_action(action_name, options)

    if not action_info:
        return jsonify(
            {
                "error": "Failed to create action",
                "reason": "Another action is already in progress.",
            }
        ), 400  # 400 Bad Request is appropriate here

    return jsonify(action_info), 200  # 200 OK or 201 Created


def clear_pois():
    """Handler for DELETE /api/core/artifact/v1/pois"""
    robot_state.pois.clear()
    print("All POIs cleared.")
    return jsonify(True)


def get_binary_map():
    """Handler for GET /api/core/slam/v1/maps/stcm"""
    # Simulate a binary map file response
    dummy_map_data = b"\xde\xad\xbe\xef" * 100  # Dummy binary data
    return Response(dummy_map_data, mimetype="application/octet-stream")


def get_localization_quality():
    """Handler for GET /api/core/slam/v1/localization/quality"""
    return Response(str(robot_state.localization_quality), mimetype="application/json")


def get_cargos():
    """Handler for GET /api/delivery/v1/cargos"""
    ret = []
    for cargo in robot_state.cargos:
        ret.append(cargo.to_dict())
    return jsonify(ret)


# A generic handler for endpoints that are not yet specifically implemented
def generic_handler(*args, **kwargs):
    print(f"Generic handler called for: {request.path} [{request.method}]")
    print(f"Path args: {kwargs}")
    if request.is_json:
        print(f"Request JSON: {request.get_json()}")

    # Return a generic success response for POST/PUT/DELETE
    if request.method in ["POST", "PUT", "DELETE"]:
        return jsonify(
            {
                "status": "success",
                "message": "Action received but not fully implemented.",
            }
        )

    # Return a generic empty object for GET
    return jsonify({"message": f"Endpoint {request.path} not fully implemented."})


def get_current_action():
    if robot_state.current_action.id != -1:
        return jsonify(robot_state.current_action)
    else:
        return jsonify("Action Not Found"), 404


def abort_current_action():
    """Handler for DELETE /api/core/motion/v1/actions/:current"""
    robot_state.abort_current_action()
    # always succeeds lol
    return jsonify({"status": "success", "message": "Action aborted."}), 200


# --- Dynamic Route Creation ---

# Mapping from operationId to our specific handler functions
# This makes the code cleaner and easier to manage.
handler_map = {
    "getPowerStatus": get_power_status,
    "getRobotInfo": get_robot_info,
    "getRobotHealth": get_robot_health,
    "shutdown": shutdown_robot,
    "getPose": get_pose,
    "getLocalizationQuality": get_localization_quality,
    "setPose": set_pose,
    "getCurrentPois": get_current_pois,
    "addPois": add_poi,
    "deletePoi": delete_poi,
    "clearPois": clear_pois,
    "getCompositeMap": get_binary_map,
    "getCargos": get_cargos,
    "getCurrentAction": get_current_action,
    "createAction": create_action,
    "abortCurrentAction": abort_current_action,
}


def create_routes_from_spec(app, spec_file):
    """
    Reads the OpenAPI spec and dynamically creates Flask routes.
    """
    with open(spec_file, "r", encoding="utf-8") as f:
        spec = json.load(f)

    for path, path_item in spec["paths"].items():
        flask_path = convert_path_to_flask(path)

        for method, operation in path_item.items():
            if method.lower() in ["get", "post", "put", "delete"]:
                operation_id = operation.get("operationId")
                summary = operation.get("summary", "No summary")

                # Choose the handler function
                if operation_id and operation_id in handler_map:
                    handler_func = handler_map[operation_id]
                else:
                    handler_func = generic_handler

                # Use the operationId as the endpoint name for Flask
                endpoint_name = f"{method}_{path.replace('/', '_')}"

                # Add the rule to the app
                app.add_url_rule(
                    flask_path,
                    endpoint=endpoint_name,
                    view_func=handler_func,
                    methods=[method.upper()],
                )
                print(
                    f"Created route: {method.upper():<7} {flask_path:<60} -> {handler_func.__name__:<20} ({summary})"
                )


if __name__ == "__main__":
    # Load the configuration and create all routes
    create_routes_from_spec(app, "swagger-conf.json")

    # Run the Flask development server
    app.run(host="0.0.0.0", port=1448, debug=True)
