#ifndef GAMESTATE_H
#define GAMESTATE_H

#include <string>
#include <stdint.h>

namespace Connect4_AI{
    /** Reference:- http://blog.gamesolver.org/solving-connect-four/06-bitboard/
                 :- https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0
                 :- https://github.com/denkspuren/BitboardC4/blob/master/BitboardDesign.md

    * A class storing a Connect 4 position.
    * Functions and position are relative to the current player to play.

    * A binary bitboard representationis used.
    * Each column is encoded on HEIGHT+1 bits, use of one exta bit in each 
    * column is to avoid warping around => rows already have extra bits on right
     
    * Example of bit order to encode for a 7x6 board
      .  .  .  .  .  .  .
      5 12 19 26 33 40 47
      4 11 18 25 32 39 46
      3 10 17 24 31 38 45
      2  9 16 23 30 37 44
      1  8 15 22 29 36 43
      0  7 14 21 28 35 42 
      
    * GameState is stored as
     - a bitboard "mask" with 1 on any color stones
     - a bitboard "current_player" with 1 on stones of current player

    * "current_player" bitboard can be transformed into a compact and non ambiguous key
    * by adding an extra bit on top of the last non empty cell of each column.
    * This allow to identify all the empty cells whithout needing "mask" bitboard
    *
     * current_player "x" = 1, opponent "o" = 0
     * board     position  mask      key       bottom
     *           0000000   0000000   0000000   0000000
     * .......   0000000   0000000   0001000   0000000
     * ...o...   0000000   0001000   0010000   0000000
     * ..xx...   0011000   0011000   0011000   0000000
     * ..ox...   0001000   0011000   0001100   0000000
     * ..oox..   0000100   0011100   0000110   0000000
     * ..oxxo.   0001100   0011110   1101101   1111111
     *
     * current_player "o" = 1, opponent "x" = 0
     * board     position  mask      key       bottom
     *           0000000   0000000   0001000   0000000
     * ...x...   0000000   0001000   0000000   0000000
     * ...o...   0001000   0001000   0011000   0000000
     * ..xx...   0000000   0011000   0000000   0000000
     * ..ox...   0010000   0011000   0010100   0000000
     * ..oox..   0011000   0011100   0011010   0000000
     * ..oxxo.   0010010   0011110   1110011   1111111
     *
     * key is an unique representation of a board key = position + mask + bottom
     => Logic of the formula, 
            * bottom + mask results in all bitboard with 1 at topmost
            unused position in a column. (That's because column's bottom bit is the least
            significant bit of that column)
            * Then, adding position to it finally result in our desired key.
     => Although actual key is position + mask + bottom, but bottom is a constant so position + mask
        is also a unique unambiguos respresentation
     */
    class GameState{
        private:
            uint64_t current_position;
            uint64_t mask;
            int moves;

            /**
            * Test 4-alignment for current player (identified by one in the bitboard pos)
            * @param a bitboard position of a player's cells.
            * @return true if the player has a 4-alignment.
            */
            static bool alignment(uint64_t pos); 


            // return a bitmask containg a single 1 corresponding to the top cel of a given column
            static constexpr uint64_t top_mask_col(int col) {
                return UINT64_C(1) << ((HEIGHT - 1) + col*(HEIGHT+1));
            }


            // return a bitmask containg a single 1 corresponding to the bottom cell of a given column
            static constexpr uint64_t bottom_mask_col(int col) {
                return UINT64_C(1) << col*(HEIGHT+1);
            }


            // count set bits in a 64 bit integer
            static int count_set_bits(uint64_t n){
                int count = 0; 
                while(n!=0){ n = n&(n-1); count++; }
                return count; 
            }

        public:
            GameState();

            static const int WIDTH  = 7;
            static const int HEIGHT = 6;
            static const uint64_t bottom_mask = 1 + (1LL << (HEIGHT+1)) + (1LL << 2*(HEIGHT+1)) + (1LL << 3*(HEIGHT+1)) + (1LL << 4*(HEIGHT+1)) + (1LL << 5*(HEIGHT+1)) + (1LL << 6*(HEIGHT+1));
            static const uint64_t board_mask  = bottom_mask * ((1LL << HEIGHT)-1);


            void playCol(int col);
            void playMove(uint64_t move);
            uint64_t possible() const;
            unsigned int play(std::string seq);
            uint64_t unique_key() const;
            int nbMoves() const;
            uint64_t possibleNonLosingMoves() const;
            bool canWinNext() const;
            bool isWinningMove(int col) const;

            static constexpr uint64_t column_mask(int col){
                return ((UINT64_C(1) << HEIGHT)-1) << col*(HEIGHT+1);
            }
            
            bool canPlay(int col) const{
                return ((mask & top_mask_col(col)) == 0);
            }

            int moveScore(uint64_t move) const{
                return count_set_bits(compute_winning_position(current_position | move, mask));
            }

            uint64_t winning_position() const{
                return compute_winning_position(current_position, mask);
            }

            uint64_t opponent_winning_position() const{
                return compute_winning_position(current_position ^ mask, mask);
            }


            /*
            * @parmam position, a bitmap of the player to evaluate the winning pos
            * @param mask, a mask of the already played spots
            *
            * @return a bitmap of all the winning free spots making an alignment
            */
            static uint64_t compute_winning_position(uint64_t position, uint64_t mask);

            
  };
}

#endif