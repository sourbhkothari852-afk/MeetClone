from channels.generic.websocket import AsyncWebsocketConsumer
import json


class MeetingConsumer(
    AsyncWebsocketConsumer
):

    async def connect(self):

        self.meeting_id = (
            self.scope["url_route"]["kwargs"]
            ["meeting_id"]
        )

        self.room_group_name = (
            f"meeting_{self.meeting_id}"
        )

        print(
            f"[MEETING] Connecting: "
            f"meeting={self.meeting_id}"
        )

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

        print(
            f"[MEETING] WebSocket connected: "
            f"meeting={self.meeting_id}"
        )


    async def disconnect(
        self,
        close_code
    ):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        print(
            f"[MEETING] WebSocket disconnected: "
            f"meeting={self.meeting_id}, "
            f"code={close_code}"
        )


    async def receive(
        self,
        text_data
    ):

        print(
            f"[MEETING] Received: "
            f"{text_data}"
        )

        # =============================================
        # PARSE JSON
        # =============================================

        try:

            message = json.loads(
                text_data
            )

        except json.JSONDecodeError:

            print(
                "[MEETING] Plain text signaling message"
            )

            await self.channel_layer.group_send(

                self.room_group_name,

                {
                    "type":
                        "meeting_message",

                    "message":
                        text_data,
                },
            )

            return


        message_type = message.get(
            "type"
        )


        # =============================================
        # END MEETING
        # =============================================

        if message_type == "end_meeting":

            print(
                f"[MEETING] END MEETING received: "
                f"meeting={self.meeting_id}"
            )

            await self.channel_layer.group_send(

                self.room_group_name,

                {
                    "type":
                        "meeting_ended",

                    "message":
                        json.dumps({

                            "type":
                                "meeting_ended",

                            "message":
                                "Meeting ended by host.",

                        }),
                },
            )

            print(
                f"[MEETING] meeting_ended broadcast sent: "
                f"meeting={self.meeting_id}"
            )

            return


        # =============================================
        # NORMAL SIGNALING
        # =============================================

        await self.channel_layer.group_send(

            self.room_group_name,

            {
                "type":
                    "meeting_message",

                "message":
                    text_data,
            },
        )


    # =============================================
    # NORMAL MEETING MESSAGE
    # =============================================

    async def meeting_message(
        self,
        event
    ):

        await self.send(

            text_data=
                event["message"]

        )


    # =============================================
    # MEETING ENDED
    # =============================================

    async def meeting_ended(
        self,
        event
    ):

        print(
            f"[MEETING] Sending meeting_ended "
            f"to client: meeting={self.meeting_id}"
        )

        await self.send(

            text_data=
                event["message"]

        )