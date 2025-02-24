# Gmail Agent

Gmail Agent is an AI-powered tool that interacts with Gmail to help automate email tasks such as sending, reading, and organizing emails. It leverages the Gmail API to integrate seamlessly with your Gmail account, empowering you to manage your inbox with ease.

## Features

- **AI-Powered Email Management:** Send emails, read messages, and organize your inbox using natural language commands.
- **Automation:** Automate routine email tasks and improve your productivity.
- **Intuitive Interaction:** Receive intelligent suggestions and responses to streamline your email workflow.

## Prerequisites

- **Python:** Depending on your project setup. Ensure you have Python installed.
- **Gmail API Credentials:** You must obtain credentials from the Google Cloud Console. Follow the [Gmail API Quickstart Guide](https://developers.google.com/gmail/api/quickstart) to get started.

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vpavasovcase/gmail-agent.git
   cd gmail-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Gmail API Credentials:**
   - Obtain your credentials by following the Gmail API guide on the [Google Developers site](https://developers.google.com/gmail/api/quickstart).
   - Place your `credentials.json` file in the project root (or follow your project documentation if different).
   - Optionally, create a `.env` file with the following content to define the credentials path:
     ```env
     GMAIL_CREDENTIALS=./credentials.json
     ```

## Usage

After completing the setup, you can start the Gmail Agent with the following command:
```bash
python main.py
```

Follow the on-screen instructions to authenticate with Gmail. Once authenticated, you can interact with the agent using natural language commands to send emails, read your inbox, and perform various email management tasks.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for improvements or bug fixes. Ensure your code follows the project's coding standards.

## License

This project is licensed under the MIT License.
