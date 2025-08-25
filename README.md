### Django React OpenAI Chat

A chat app build with Django and React that calls the OpenAI API.

#### Set environment variables

Create a `.env` file in the `backend` folder containing the following:

```
OPENAI_API_KEY=
OPENAI_MODEL=
```

The model is optional, it will default to `gpt-3.5-turbo` if no value is provided.

#### Run the project

To run the project:

```
docker-compose up -d
```

Then visit `localhost:5173` in your browser.
