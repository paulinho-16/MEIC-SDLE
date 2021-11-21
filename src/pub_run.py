from publisher import Publisher

if __name__ == '__main__':
    pub = Publisher(4)
    try:
        pub.run()
    except KeyboardInterrupt:
        pass