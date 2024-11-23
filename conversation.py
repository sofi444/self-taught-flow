import asyncio
import io
import ssl
import sys

import pyaudio

from speechmatics_flow.client import WebsocketClient
from speechmatics_flow.models import (
    ConnectionSettings,
    Interaction,
    AudioSettings,
    ConversationConfig,
    ServerMessageType,
)

import os
from dotenv import load_dotenv
load_dotenv()

CHUNK_SIZE = 1024  # default 256
SEE_TRANSCRIPTS = True
AUTH_TOKEN = os.getenv("SPEECHMATICS_API_KEY")

# SSL (Secure Sockets Layer) Configuration
# Dummy SSL context to disable hostname and certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = WebsocketClient(
    ConnectionSettings(
        url="wss://flow.api.speechmatics.com/v1/flow",
        auth_token=AUTH_TOKEN,
        ssl_context=ssl_context,
    )
)

# Store audio messages in a queue (for playback)
audio_queue = asyncio.Queue()

# Handle server messages
def message_handler(msg: dict):
    if isinstance(msg, dict):
        message_type = msg.get("message", "")
        
        # Only process final transcripts, not partials
        if message_type == "AddTranscript":
            if "metadata" in msg and "transcript" in msg["metadata"]:
                transcript = msg["metadata"]["transcript"]
                if transcript.strip() and SEE_TRANSCRIPTS:
                    print(f"User: {transcript}")
        
        # Flow response completed
        elif message_type == "ResponseCompleted":
            content = msg.get("content", "")
            if content and SEE_TRANSCRIPTS:
                print(f"AI (completed): {content}")
        
        # Flow response interrupted
        elif message_type == "ResponseInterrupted":
            content = msg.get("content", "")
            if content and SEE_TRANSCRIPTS:
                print(f"AI (interrupted): {content}")

# Handle binary audio messages from the server
def binary_msg_handler(msg: bytes):
    if isinstance(msg, (bytes, bytearray)):
        audio_queue.put_nowait(msg)

# Catch and log issues
def error_handler(msg: dict):
    if isinstance(msg, dict):
        message_type = msg.get("message", "")
        details = msg.get("details", "")
        if message_type == "Error":
            print(f"Error: {details}")
        elif message_type == "Warning":
            print(f"Warning: {details}")

# Register handlers
client.add_event_handler(ServerMessageType.AddAudio, binary_msg_handler)
client.add_event_handler(ServerMessageType.AddTranscript, message_handler)
client.add_event_handler(ServerMessageType.ResponseCompleted, message_handler)
client.add_event_handler(ServerMessageType.ResponseInterrupted, message_handler)
client.add_event_handler(ServerMessageType.Error, error_handler)
client.add_event_handler(ServerMessageType.Warning, error_handler)

async def audio_playback():
    '''Continuously read from the audio queue and play audio back to the user.'''
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)

    try:
        while True:
            # Create a new playback buffer for each iteration
            playback_buffer = io.BytesIO()

            # Fill the buffer up to the chunk size
            while playback_buffer.tell() < CHUNK_SIZE:
                data = await audio_queue.get()
                playback_buffer.write(data)

            # Write the full buffer contents to the player stream
            stream.write(playback_buffer.getvalue())
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

async def main():
    '''
    1. Sets up microphone input
    2. Configures AI conversation
    3. Manages concurrent audio playback
    '''
    tasks = [
        asyncio.create_task(
            client.run(
                interactions=[Interaction(sys.stdin.buffer)],
                audio_settings=AudioSettings(
                    encoding="pcm_s16le",  # default
                    sample_rate=16000,  # default
                    chunk_size=CHUNK_SIZE,
                ),
                conversation_config=ConversationConfig(
                    #template_id="flow-service-assistant-amelia",
                    template_id="flow-service-assistant-humphrey",
                    template_variables={
                        "persona": "Your name is Jojo. You are a witty young man who makes a lot of dad jokes and puns.",
                        "style": "Your tone makes people feel at ease and comfortable.",
                        "context": "You are having a conversation. You want to entertain and make the other person laugh.",
                    },
                ),
            )
        ),
        asyncio.create_task(audio_playback()),
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())