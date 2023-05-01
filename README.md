
# Socket Communication and File Sending

## Background

The was a project I had for a second year networking class in university. The project was to make a 
simple socket connection for downloading files from a central server. I remember having a lot of time of my 
hands as this was an assignment during COVID times. I had seen 'fancy' logging done before but I guessed it was a print statement.
I find my logging style in this project to be rigorous yet hilarious.

### Key Learnings

 - Understanding on TCP/IP connections,
 - Experience with bitwise operations, 
 - Early experience with python libraries.

### Future Reflection (May 2023)

Looking back on this project I am realising just how valuable it was. Now that I use websockets often in applications,
I have a greater appreciation for what I learnt here. I also like that we used bitwise operations as to not cut corners. 
I think this was super valuable for my learning. I would like to try and make a more rigorous version of something like this,
possibly with more complex filetypes than a text file. 


## Usage

#### Server side
The server side must be running first. To get the server to start listening use the commands:

```shell

cd server
python3 server.py 9000

```
<sub>Note that 9000 just represents a port number, you can use any port as long as its consistent between the server and client. </sub>

#### Client side

To run the client side:

```shell
cd client
python3 client.py 127.0.1.1 9000 example.txt
```