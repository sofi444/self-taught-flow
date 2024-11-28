## Speech to Speech Conversation with Speechmatics Flow 🌀


*coming soon: use Flow to facilitate self-learning from online videos


`python conversation.py` to chat with Jojo - he thinks he's funny... 


Speechmatics are known for their high-quality multilingual Automatic Speech Recognition. Flow is their conversational API (_early access_ at the time of writing!).

Flow supports **speaker diarization**, which means that based on acoustic features, it can detect multiple speakers in a conversation and keep track of speaker-specific information! 

And you can play around with the _persona_, _style_, and _context_ parameters to create your own character!

Turn on/off the transcripts by setting `SEE_TRANSCRIPTS = False`.


<img width="500" alt="Screenshot 2024-11-28 at 23 27 33" src="https://github.com/user-attachments/assets/1a4ad675-0d1c-4a68-a7ee-34cb841a243c">

--

Some downsides I noticed:
- LLM component related mistakes. Hard to pinpoint without knowing their architecture exactly, but point is: it misunderstands often.
- Not possible to control voice style during the conversation.
- The default voice _amelia_ is painful to my ears.
  
<img width="500" alt="Screenshot 2024-11-28 at 22 52 05" src="https://github.com/user-attachments/assets/ab9d2c45-2456-4407-b73a-faf47f94a450">

--

😮 \
<img width="300" alt="Screenshot 2024-11-23 at 15 51 21" src="https://github.com/user-attachments/assets/c14f5b98-8e89-4eda-b52f-e414d44093cd">



Check out Flow: https://www.speechmatics.com/flow

API Docs: https://docs.speechmatics.com/flow/getting-started
