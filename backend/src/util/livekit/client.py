import os

from livekit import RoomServiceClient

client = RoomServiceClient(os.getenv("LIVEKIT_URL"), os.getenv("LIVEKIT_KEY"), os.getenv("LIVEKIT_SECRET"))
