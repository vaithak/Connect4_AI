# Connect4 Online Multiplayer Game with AI Bot

[Live Link - play here](https://con-4.herokuapp.com)   

### Features  
  * **Play against AI**  
  * **Compete against friends** by sharing game code with them  
  * **Spectate games** - multiple people can join the same game using game code, while only two will play others can spectate the game  
  * **Inbuilt chatting feature** - Anyone who has joined the game(whether playing or spectating) can chat along.  
  
### Build locally
Requirements - python 3, pip, gcc version 4.8+  

  * Clone the repo and cd into the cloned directory  
      `git clone https://github.com/vaithak/Connect4_AI.git`  
  * Install the dependencies  
      `pip install -r requirements.txt`  
  * Build the shared library for AI module written in C++  
     `python setup.py build_ext --build-lib connect4_game/`  
  * Start the server  
     `python manage.py runserver`  
<hr>   

### Some bugs to fix
- Currently, the application allows both players to have same usernames which results in a deadlock for moves.

### References  
  - [Django Channels](https://channels.readthedocs.io/en/latest/)  
  - [Connect Four - Wikipedia](https://en.wikipedia.org/wiki/Connect_Four)  
  - [http://people.csail.mit.edu/plaat/mtdf.html](http://people.csail.mit.edu/plaat/mtdf.html)  
  - [http://web.mit.edu/sp.268/www/2010/connectFourSlides.pdf](http://web.mit.edu/sp.268/www/2010/connectFourSlides.pdf)  
  - [Bitboard Representation - 1](http://blog.gamesolver.org/solving-connect-four/06-bitboard/)   
  - [Birboard Reprsentation - 2](https://github.com/denkspuren/BitboardC4/blob/master/BitboardDesign.md)  
  - [Transposition Tables](http://blog.gamesolver.org/solving-connect-four/07-transposition-table/)  
  - [Null window search](https://cs.stackexchange.com/questions/1134/how-does-the-negascout-algorithm-work)  

