<h1>
<img src="icon.png" width=100/>
  
Note to Flashcard
</h1>

Convert freeform notes into flashcards, exported in CSV format and ideal for Anki. Bring your own OpenAI API token. Sensible defaults are used.

This project uses OpenAI's [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) to produce valid JSON which follows a predefined
schema, and then converts this to the CSV format. Users can assign tags as well (space-separated for Anki).

Currently, only the 'Basic' flashcard type is supported with a Question and then an Answer.

Downloads are available at [Releases](https://github.com/olliecheng/note-to-flashcard/releases). Note that due to stricter Gatekeeper requirements on macOS 15, it is harder to run unnotarised applications. [See the official Apple guidance on running Mac apps from unknown developers](https://support.apple.com/en-au/guide/mac-help/mh40616/mac).

<div align="center">
  <img width="680" src="https://github.com/user-attachments/assets/730e8663-9d82-4456-8368-2bb0c92a669e"/>
</div>
