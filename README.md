[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/espressif/docs-bot-action/master.svg)](https://results.pre-commit.ci/latest/github/espressif/docs-bot-action/master)


# Github Action for replying to issues

This action is limited to the `espressif` Github namespace and cannot be used outside of this organization.
The project is experimental. Please open issues if you encounter any.

The action uses the Espressif Chatbot and its knowledge base for automatically answering Github issues.

## How to use it

Here is an example how to create a workflow in the project:


```yaml
name: Bot response

on:
  issues:
    types: [opened, edited]

jobs:
  docs_bot:
    name: Generate automated response by docs bot
    runs-on: ubuntu-latest
    steps:
      - name: Docs bot action
        # use this check against the espressif namespace in order to avoid failures in forked projects
        if: ${{ github.repository_owner == 'espressif' }}
        uses: espressif/docs-bot-action@master
        env:
            BOT_API_KEY: ${{ secrets.BOT_API_KEY }}
            BOT_INTEGRATION_ID: ${{ secrets.BOT_INTEGRATION_ID }}
            BOT_API_ENDPOINT: ${{ secrets.BOT_API_ENDPOINT }}
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          github_repository: ${{ github.repository }}
          github_issue_number: ${{ github.event.issue.number }}
          in_msg: ${{ github.event.issue.body }}
          title: ${{ github.event.issue.title }}
          prefix_out_msg: >
            Hi @${{ github.event.issue.user.login }}! This is an automated answer.
```

## Limitations

- One cannot communicate with the bot. Only one response is generated based on the issue body. The bot will not
  respond to comments.
