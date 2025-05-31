import asyncio
import aiofiles
from tensorflow.keras import Model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from typing import List
import pickle

THRESHOLD = 0.65
MAX_SEQUENCE_LENGTH = 100
MODEL_PATH = r"spam_model\outputs\SpamDetectorModel.keras"
TOKENIZER_PATH = r"spam_model\outputs\tokenizer.pickle"

tokenizer: Tokenizer | None = None
model: Model | None = None

async def load():
    """
    Load the trained spam detection model and tokenizer asynchronously.

    This function loads the Keras model from the given MODEL_PATH and
    asynchronously reads and deserializes the tokenizer pickle file from TOKENIZER_PATH.
    The loaded model and tokenizer are stored in global variables.

    """
    global model, tokenizer
    model = load_model(MODEL_PATH)

    async with aiofiles.open(TOKENIZER_PATH, "rb") as f:
        content = await f.read()
        tokenizer = pickle.loads(content)
    
async def preprocess(text: List[str]):
    """
    Preprocess a list of text strings into padded sequences suitable for model input.
    
    """
    sequences = tokenizer.texts_to_sequences(text)
    padded = pad_sequences(
        sequences,
        maxlen=MAX_SEQUENCE_LENGTH,
        padding="post"
    )

    return padded

async def spam(text: str) -> List[str]:
    """
    Predict whether the given text is spam or not.
    """
    # preprocess text
    preprocessed = await preprocess([text])
    prediction = model.predict(preprocessed)
    return prediction >= THRESHOLD

asyncio.run(load())