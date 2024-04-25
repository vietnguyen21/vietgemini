import google.generativeai as genai
import textwrap

def to_markdown(text):
  text = text.replace('•', '  *')
  return textwrap.indent(text, '> ', predicate=lambda _: True)

API_key = 'AIzaSyA2BZg4Ngyb5x1F0HwYrFXCr0gzXbv1ZT0'

def generative_text(input):
    genai.configure(api_key=API_key)

    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content(input)
        return to_markdown(response.text)
    except ValueError as e:
        # Handle the error when response.text is inaccessible
        if 'safety_ratings' in str(e):
            print("Error: Text generation might be blocked due to safety concerns.")
            print("Review your input text and consider contacting the Generative AI service for more information.")
        else:
            print(f"An error occurred: {e}")
        return None  # Indicate error or return an alternative value
