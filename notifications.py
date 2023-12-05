from mailjet_rest import Client
import os


def reply_mail(name, email):
    api_key = os.environ.get("MJ_APIKEY_PRIVATE")
    # os.environ.get("MJ_APIKEY_PRIVATE")
    api_secret = os.environ.get("MJ_APIKEY_PUBLIC")

    # os.environ.get("MJ_APIKEY_PRIVATE")
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "humble.py.test@gmail.com",
                    "Name": "Me"
                },
                "To": [
                    {
                        "Email": f"{email}",
                        "Name": "You"
                    }
                ],
                "Subject": "REPLY FROM POST LAND!",
                "TextPart": f"Dear {name}\n\nWe have received your message and our response would be sent to you soon."
                            f"Thank you\n\nPOST LAND TEAM",
                "HTMLPart": ""
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())


def send_email(user_name, user_email, tel, msg):
    api_key = os.environ.get("MJ_APIKEY_PRIVATE")
    # os.environ.get("MJ_APIKEY_PRIVATE")
    api_secret = os.environ.get("MJ_APIKEY_PUBLIC")
    # os.environ.get("MJ_APIKEY_PUBLIC")
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "humble.py.test@gmail.com",
                    "Name": "Me"
                },
                "To": [
                    {
                        "Email": "humble.py.test@gmail.com",
                        "Name": "You"
                    }
                ],
                "Subject": "NEW TEDDY SHOP MESSAGE!",
                "TextPart": f"User Information!\n\nNAME: {user_name} \n\nEMAIL: {user_email}\n\n"
                            f"Tell: {tel}\n\nMessage:\n\n{msg}",
                "HTMLPart": ""
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
    reply_mail(name=user_name, email=user_email)


def send_code(username, msg, email):
    api_key = os.environ.get("MJ_APIKEY_PRIVATE")
    # os.environ.get("MJ_APIKEY_PRIVATE")
    api_secret = os.environ.get("MJ_APIKEY_PUBLIC")
    # os.environ.get("MJ_APIKEY_PUBLIC")
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "humble.py.test@gmail.com",
                    "Name": "Me"
                },
                "To": [
                    {
                        "Email": f"{email}",
                        "Name": "You"
                    }
                ],
                "Subject": "TEDDY SHOP Modification Code!!!",
                "TextPart": f"Dear {username}\n\nCODE:\n\n{msg}",
                "HTMLPart": ""
            }
        ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
