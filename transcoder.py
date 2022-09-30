import threading
from six.moves import queue
from google.cloud import speech
from google.cloud.speech_v1 import types


class Transcoder(object):
    """
    Converts audio chunks to text
    """

    def __init__(self, encoding, rate, language):
        self.buff = queue.Queue()
        self.encoding = encoding
        self.language = language
        self.rate = rate
        self.closed = True
        self.transcript = None

    def start(self):
        """Start up streaming speech call"""
        threading.Thread(target=self.process).start()

    def response_loop(self, responses):
        """
        Pick up the final result of Speech to text conversion
        """
        for response in responses:
            if not response.results:
                continue
            result = response.results[0]
            if not result.alternatives:
                continue
            transcript = result.alternatives[0].transcript
            if result.is_final:
                self.transcript = transcript

    def process(self):
        """
        Audio stream recognition and result parsing
        """
        # You can add speech contexts for better recognition
        cap_speech_context = types.SpeechContext(phrases=["Add your phrases here"])
        client = speech.SpeechClient()
        print("Speech Client")
        config = types.RecognitionConfig(
            encoding=self.encoding,
            sample_rate_hertz=self.rate,
            language_code=self.language,
            speech_contexts=[cap_speech_context, ],
            model='command_and_search'
        )
        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
            single_utterance=False)
        audio_generator = self.stream_generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)
        try:
            self.response_loop(responses)
        except:
            self.start()

    def stream_generator(self):
        while not self.closed:
            chunk = self.buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self.buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b''.join(data)

    def write(self, data):
        """
        Writes data to the buffer
        """
        self.buff.put(data)
