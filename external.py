from openai import AsyncOpenAI

async def make_json(key: str, notes: str) -> str:
    client = AsyncOpenAI(
        api_key=key
    )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a helpful assistant who must make flashcards from the provided notes. You must be thorough and include everything - DO NOT OMIT ANY DETAILS. A key goal should be for the answer to each flashcard to be short and concise; a good inspiration is to follow the core principles of Piotr Wozniak and Supermemo/Anki. The flashcards should be optimised for retention using a spaced repetition system like Anki. Answers should be in dot point form if appropriate.\n\nFor complex facts, breaking them up into multiple smaller flashcards is ideal."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": notes
                    }
                ]
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "flashcards",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "flashcards": {
                            "type": "array",
                            "description": "A collection of flashcards, each containing a question and an answer.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {
                                        "type": "string",
                                        "description": "The question posed on the flashcard."
                                    },
                                    "answer": {
                                        "type": "string",
                                        "description": "The answer corresponding to the question on the flashcard."
                                    }
                                },
                                "required": [
                                    "question",
                                    "answer"
                                ],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": [
                        "flashcards"
                    ],
                    "additionalProperties": False
                }
            }
        },
        temperature=1,
        max_completion_tokens=10000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content