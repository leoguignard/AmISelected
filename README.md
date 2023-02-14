# Am I Selected?

Well are you?

You can run the following command to get an email when your status changed in the coudert webpage:
```shell
python read_html.py --sections 7 8 9 \
    --name lastname firstname \
    --year 2023 \
    --username your_username \
    --password your_sending_email_pwd \
    --smtp smtp.your.server.com \
    --port 587 \
    --recipient you@mail.com \
```