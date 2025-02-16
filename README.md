<h1>
<img src="icon.png" width=100/>
  
Note to Flashcard
</h1>

Convert freeform notes into flashcards, exported in CSV format and ideal for Anki. Bring your own OpenAI API token. Sensible defaults are used.

This project uses OpenAI's [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) to produce valid JSON which follows a predefined
schema, and then converts this to the CSV format. Users can assign tags as well (space-separated for Anki).

Currently, only the 'Basic' flashcard type is supported with a Question and then an Answer.

<img width="579" alt="image" src="https://github.com/user-attachments/assets/97de49cb-7783-4ace-9df0-c34049dbfbdd" />
