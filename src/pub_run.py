from publisher import Publisher

if __name__ == '__main__':
    pub = Publisher()
    try:
        pub.run()
    except KeyboardInterrupt:
        pass