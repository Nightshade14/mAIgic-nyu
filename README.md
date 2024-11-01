# mAIgic

This project will organize life by tracking messages and information that need follow-ups and reminding the user to take follow-ups. It will also provide a search based on individuals.

The project aims to leverage AI to track and remind for follow up messages for systems like Slack, Trello, Whatsapp, Gmail, Google Docs comments, etc.

# Technical tools

- Programming Language: Python
- Project dependency management tool: uv
- Project linter: ruff
- Project tester: pytest
- Continuous Integration (CI) tool: circleCI

# Instructions

## Setup

- Install `uv` on your system with command with `curl -LsSf https://astral.sh/uv/install.sh | sh`.
- `cd` into the cloned repository and execute `uv sync` (This will install all the dependencies).
- Activate the environment `venv` by executing `source ./.venv/bin/activate`.

## Processes

- To check the formatting standard with ruff (linter) execute either `uv run ruff check .` or `ruff check .` from the root directory of the project.
- To test the code, execute either `uv run pytest .` or `pytest .` from the root directory of the project.

Note: One can run tools like ruff and pytest independently or can run them through `uv`.

## Commit Style Guide

- Request to `strictly adhere` to the suggested commit style guide.
- The project follows Udacity's [Commit Style Guide](https://udacity.github.io/git-styleguide/).
- Reason:
  - It is simple, elegant, concise and effective.
  - It does not have many rules that could create confusion but yet have just enough to keep things working smoothly through clear and concise communication.

## GitHub Workflow

- Members of same team can preferably `clone` the repository.
- Make sure to push new changes to `dev` remote branch.
- Create a `Pull Request` and the changes would be reviewed and merged to the `main` remote branch. `Review` includes code, code quality, code standards, commit style guides, and Pull Request descriptions. Consistent code standards and documentation would be aided by `ruff`.
- `main` branch serves as production branch which would accumulate new changes, features and bug-fixes from `dev` branch.
- Would appreciate if you open `issues` whenever you come across any. Issues can be bugs, proposed features, performance / code improvement proposals, etc.

## Requesting access to project and CI space

- Send your`github username` to become collaborators to the project.
- Send your `email id` used to `register with circleCI` to get access to the circleCI organization to manage CI workflows and triggers. You will receive an invitation in the provided email's inbox to join the circleCI organization.
- Currently, the `magic2` CircleCI project is attached to this project.
- Collaboration doc for this initiative: https://docs.google.com/document/d/1duhM5Ufkq_doBnMvHo65S7cplmUJw4KqQvDRfZlmj7s/edit

Note: Request to keep all `communication` in the Google Chats Project Group.

## Trello Setup

- Create a Trello account.
- Go to https://trello.com/power-ups/admin to create a new Power-up.
- Check the new power-up, click `API key` on the left side panel.
- Copy the API key and visit https://trello.com/1/authorize?expiration=1day&name=yourAppName&scope=read,write&response_type=token&key=your_api_key, replace `your_api_key` with your own api key. The expiration and the name can be changed if needed.
- Create a .env file, input your API key and token:

```
TRELLO_API_KEY=your_api_key
TRELLO_OAUTH_TOKEN=your_token
```

- Run TrelloManager.py and you will see the test result.

# License

mAIgic has a MIT-style license, as found in the [LICENSE](LICENSE) file.
