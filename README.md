# Am I Selected?

Well, are you?

## What is that?

This is a small program to automatically check whether you went thourgh the next step of the CNRS concours.

It is using the [webpage](https://www.coudert.name/concours_cnrs_2024.html) that [François-Xavier Coudert](https://twitter.com/fxcoudert) is maintaining (many thanks to him)

The command will check every 10 minutes if you status has changed from the previous time it checked.

If it has changed it will send you an email telling you whether you have progressed or not (it might be a bit sarcastic telling you).

It will always send an email every 4 hours (except at night) so you are sure that the program is still running.

## Installation

The easiest is to install it directly with `pip`:

```shell
pip install amISelected
```

## Usage

Once installed, you can run the following command:

```shell
amISelected --name lastname firstname \
            --year 2024 \
            --username your_username \
            --smtp smtp.your.server.com \
            --port 465 \
            --recipient you@mail.com \
```

Your `smtp` password will be then asked (leave empty if you don't want to recieve emails).

It might look a bit fishy ... But I don't know how to do otherwise.
The source code is available, you can still have a look at it or just not give your password.

## Troubleshooting

You can use the help of the command:

```shell
amISelected --help
```

You might have problem to recieve emails. If so, you can always use a throwaway gmail account and setup a app password as explained [there](https://support.google.com/accounts/answer/185833).
