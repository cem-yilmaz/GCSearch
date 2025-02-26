from paddleocr import PaddleOCR
import os
import re

supported_languages = [
    'en',
    'cn'
]

class OCR:
    """
    A class to perform OCR on images. Please call the `transcribe` method to perform OCR on an image.

    Args:
        language (str): The language of the text in the image. Currently supported languaged are `en` and `cn`. Defaults to 'en'.
    """
    def __init__(self, language='en'):
        if language not in supported_languages:
            raise ValueError(f'Unsupported language: \"{language}\". Supported languages are {supported_languages}.')
        self.language = language
        self.ocr_model = self.init_ocr()

    def __repr__(self):
        return f'OCR(language={self.language})'
        
    def init_ocr(self) -> PaddleOCR:
        """
        Initializes the OCR model with optimized parameters for the specified language.
        """
        if self.language == 'en':
            # Instantiating the OCR model with optimized parameters for English text
            ocr_to_use = PaddleOCR(rec_algorithm='CRNN', lang='en', use_space_char=True, drop_score=0.7)
        else:
            ocr_to_use = PaddleOCR()
        return ocr_to_use

    def transcribe(self, image_path:str) -> str | None:
        """
        Transcribes an image using the instantiated OCR model.

        Args:
            image_path (str): The path to the image file. Supported image formats are PNG, JPG, and JPEG.

        Returns:
            str: The transcribed text (None if no text is found, or if the image file does not exist/is incompatible).   
        """
        supported_formats = ['png', 'jpg', 'jpeg']
        image_file = None

        # check the extension
        if image_path.split('.')[-1] not in supported_formats:
            return None

        # Find which file exists
        if os.path.isfile(image_path):
            image_file = image_path

        if not image_file:
            return None
        
        def add_spaces(text):
            """Insert spaces where lowercase letters are followed by uppercase letters or where words are merged."""
            text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between camelCase patterns
            text = re.sub(r'(\w)([.,!?])', r'\1 \2', text)  # Add space before punctuation if merged with word
            return text
        
        data = self.ocr_model.ocr(image_file)
        if data != [None]:
            text = ''
            for line in data:
                for word in line:
                    text_line = word[-1]
                    text += text_line[0] + ' '
            cleaned_text = add_spaces(text)
        else:
            cleaned_text = None
        return cleaned_text