# Am I Selected?

Well are you?

You can run the following command to get an email when your status changed in the [coudert webpage](https://www.coudert.name/concours_cnrs_2023.html):
```shell
python read_html.py --name lastname firstname \
                    --year 2023 \
                    --username your_username \
                    --smtp smtp.your.server.com \
                    --port 587 \
                    --recipient you@mail.com \
```

Your `smtp` password will be then asked (leave empty if you don't want to recieve emails).

It looks a bit fishy because it is ... But I don't know how to do otherwise