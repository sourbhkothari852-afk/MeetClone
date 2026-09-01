import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Meeting


class MeetingConsumer(
    AsyncWebsocketConsumer
):

    async def connect(self):

        self.meeting_id = (
            self.scope["url_route"]["kwargs"]["meeting_id"]
        )

        self.room_group_name = (
            f"meeting_{self.meeting_id}"
        )

        # =================================================
        # JOIN MEETING GROUP
        # =================================================

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

        print(
            "CONNECTED:",
            self.channel_name,
            "GROUP:",
            self.room_group_name,
        )

        # =================================================
        # NOTIFY OTHER USERS
        # =================================================

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_joined",
                "channel_name": self.channel_name,
            },
        )


    async def disconnect(
        self,
        close_code
    ):

        # =================================================
        # NOTIFY OTHER USERS
        # =================================================

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_left",
                "channel_name": self.channel_name,
            },
        )

        # =================================================
        # LEAVE GROUP
        # =================================================

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        print(
            "DISCONNECTED:",
            self.channel_name,
            "GROUP:",
            self.room_group_name,
        )


    async def receive(
        self,
        text_data
    ):

        print(
            "SIGNALING RECEIVED:",
            text_data,
        )

        # =================================================
        # PARSE MESSAGE
        # =================================================

        try:

            message = json.loads(
                text_data
            )

        except json.JSONDecodeError:

            # ---------------------------------------------
            # OLD / PLAIN TEXT SIGNALING
            # ---------------------------------------------

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "signaling_message",
                    "sender": self.channel_name,
                    "message": text_data,
                },
            )

            return


        message_type = message.get(
            "type"
        )


        # =================================================
        # END MEETING
        # =================================================

        if message_type == "end_meeting":

            print(
                "END MEETING REQUESTED:",
                self.meeting_id,
            )

            # ---------------------------------------------
            # MARK MEETING AS COMPLETED
            # ---------------------------------------------

            updated = await self.complete_meeting()

            if updated:

                print(
                    "MEETING STATUS UPDATED:",
                    self.meeting_id,
                    "completed",
                )

            else:

                print(
                    "MEETING STATUS UPDATE FAILED:",
                    self.meeting_id,
                )


            # ---------------------------------------------
            # NOTIFY EVERYONE IN THE ROOM
            # ---------------------------------------------

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "meeting_ended",
                    "sender": self.channel_name,
                    "message": json.dumps({
                        "type": "meeting_ended",
                        "message": "Meeting ended by host.",
                    }),
                },
            )

            print(
                "MEETING ENDED BROADCAST SENT:",
                self.meeting_id,
            )

            return


        # =================================================
        # NORMAL WEBRTC SIGNALING
        # =================================================

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "signaling_message",
                "sender": self.channel_name,
                "message": text_data,
            },
        )


    # =====================================================
    # USER JOINED
    # =====================================================

    async def user_joined(
        self,
        event
    ):

        if (
            event["channel_name"]
            == self.channel_name
        ):
            return

        await self.send(
            text_data=json.dumps({
                "type": "user_joined",
                "message":
                    "A user joined the meeting.",
            })
        )


    # =====================================================
    # USER LEFT
    # =====================================================

    async def user_left(
        self,
        event
    ):

        if (
            event["channel_name"]
            == self.channel_name
        ):
            return

        await self.send(
            text_data=json.dumps({
                "type": "user_left",
                "message":
                    "A user left the meeting.",
            })
        )


    # =====================================================
    # NORMAL SIGNALING
    # =====================================================

    async def signaling_message(
        self,
        event
    ):

        # Do not send a user's own WebRTC signal
        # back to that same user.

        if (
            event["sender"]
            == self.channel_name
        ):
            return

        print(
            "SIGNALING SENT:",
            event["message"],
        )

        await self.send(
            text_data=event["message"]
        )


    # =====================================================
    # MEETING ENDED
    # =====================================================

    async def meeting_ended(
        self,
        event
    ):

        # Send meeting-ended event to the browser.

        print(
            "MEETING ENDED SENT TO CLIENT:",
            self.channel_name,
        )

        await self.send(
            text_data=event["message"]
        )


    # =====================================================
    # DATABASE
    # =====================================================

    @database_sync_to_async
    def complete_meeting(
        self
    ):

        try:

            meeting = Meeting.objects.get(
                id=self.meeting_id
            )

        except Meeting.DoesNotExist:

            return False


        # ---------------------------------------------
        # ONLY CHANGE IF NOT ALREADY COMPLETED
        # ---------------------------------------------

        if meeting.status != "completed":

            meeting.status = "completed"

            meeting.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return True