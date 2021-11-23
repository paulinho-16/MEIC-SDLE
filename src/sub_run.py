from subscriber import Subscriber

if __name__ == "__main__":
    new_client = Subscriber(1)
    try:
        new_client.run()
    except KeyboardInterrupt:
        pass