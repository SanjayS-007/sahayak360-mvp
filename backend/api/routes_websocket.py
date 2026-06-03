"""
WebSocket routes — real-time quiz dispatch and completion notifications.
"""

import json
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query

router = APIRouter()


class StudentConnectionManager:
    """Manages per-student WebSocket connections for targeted quiz dispatch."""

    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, student_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[student_id] = websocket

    def disconnect(self, student_id: str):
        self.connections.pop(student_id, None)

    async def send_to_student(self, student_id: str, message: dict) -> bool:
        """Send message to a specific student. Returns True if delivered."""
        ws = self.connections.get(student_id)
        if ws:
            try:
                await ws.send_json(message)
                return True
            except Exception:
                self.disconnect(student_id)
                return False
        return False

    async def broadcast_to_class(self, student_ids: list[str], message: dict):
        """Broadcast message to multiple students."""
        for sid in student_ids:
            await self.send_to_student(sid, message)

    @property
    def online_students(self) -> list[str]:
        return list(self.connections.keys())


ws_manager = StudentConnectionManager()


@router.websocket("/student/{student_id}")
async def student_websocket(
    websocket: WebSocket,
    student_id: str,
    token: str = Query(default=""),
):
    """
    WebSocket endpoint for student real-time communication.
    Handles: quiz dispatch, progress updates, notifications.
    """
    # Token validation (simplified for MVP — full validation in production)
    from auth.jwt_handler import verify_token
    payload = verify_token(token)
    if not payload or payload.get("sub") != student_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await ws_manager.connect(student_id, websocket)
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "student_id": student_id,
            "message": "Real-time connection established",
        })

        # Listen for messages from student
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type", "unknown")

                if msg_type == "quiz_response":
                    # Student submitted a quiz answer in real-time
                    await websocket.send_json({
                        "type": "ack",
                        "message": "Response received",
                        "question_id": message.get("question_id"),
                    })

                elif msg_type == "heartbeat":
                    await websocket.send_json({"type": "heartbeat_ack"})

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}",
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(student_id)


@router.websocket("/teacher/{teacher_id}")
async def teacher_websocket(
    websocket: WebSocket,
    teacher_id: str,
    token: str = Query(default=""),
):
    """
    WebSocket for teacher — receives completion notifications and class updates.
    """
    from auth.jwt_handler import verify_token
    payload = verify_token(token)
    if not payload or payload.get("sub") != teacher_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()
    try:
        await websocket.send_json({
            "type": "connected",
            "teacher_id": teacher_id,
            "online_students": ws_manager.online_students,
        })

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "dispatch_quiz":
                # Teacher dispatches quiz to student via WebSocket
                target_student = message.get("student_id")
                quiz_data = message.get("quiz_data", {})
                delivered = await ws_manager.send_to_student(target_student, {
                    "type": "quiz_dispatch",
                    "data": quiz_data,
                })
                await websocket.send_json({
                    "type": "dispatch_result",
                    "student_id": target_student,
                    "delivered": delivered,
                })

    except WebSocketDisconnect:
        pass


def get_ws_manager() -> StudentConnectionManager:
    """Dependency to access WebSocket manager."""
    return ws_manager
