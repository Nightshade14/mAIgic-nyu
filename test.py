from src.gmail.client import Gmail

# this is used for init Gmail and generate token.json
def main():

    # Initialize the Gmail client
    gmail = Gmail()
    
    messages = list(gmail.query())
    print(f"You have {len(messages)} messages in your inbox.")
    # print(gmail.get_message('19291cab0733afc1'))

if __name__ == "__main__":
    main()