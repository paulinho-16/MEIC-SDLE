# SDLE Project

SDLE Project for group T3G13.

Group members:

1. Diogo Samuel Fernandes (up201806250@fe.up.pt)
2. Hugo Guimarães (up201806490@fe.up.pt)
3. Paulo Ribeiro (up201806505@fe.up.pt)
4. Telmo Baptista (up201806554@fe.up.pt)

## Instructions 

> See the Makefile inside the src folder for more information

1. Clone this repository:
   `git clone https://git.fe.up.pt/sdle/2021/t3/g13/proj1.git`

2. In the `proj1` directory:

For Windows:

- Create the Virtual Environment: `py -m venv env`
- Activate the Virtual Environment: `.\env\Scripts\activate.bat`
- Install the requirements: `pip install -r requirements.txt`

For Linux:

- Create the Virtual Environment: `python -m venv env`
- Activate the Virtual Environment: `source env/bin/activate`
- Install the requirements: `pip install -r requirements.txt`

3. Run the Proxy:
   `make proxy`

4. Run a publisher:
   `make publisher`

5. Run a subscriber:
   `make subscriber`

6. Publish a message of a new topic:
   `make put`

7. Get a message from a given topic:
   `make get`

8. Subscribe a new topic:
   `make sub`

9. Unsubscribe a given topic:
   `make unsub`

10. Clear all the output files:
   `make clean`