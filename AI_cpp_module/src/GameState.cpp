#include "GameState.h"
#include <stdint.h>

using namespace Connect4_AI;

bool GameState::alignment(uint64_t pos) {
    // Intiial steps are done to avoid warping

    // horizontal 
    uint64_t temp = pos & (pos >> (HEIGHT+1));
    if(temp & (temp >> (2*(HEIGHT+1)))) return true;

    // diagonal 1 
    temp = pos & (pos >> HEIGHT);
    if(temp & (temp >> (2*HEIGHT))) return true;

    // diagonal 2
    temp = pos & (pos >> (HEIGHT+2));
    if(temp & (temp >> (2*(HEIGHT+2)))) return true;

    // vertical;
    temp = pos & (pos >> 1);
    if(temp & (temp >> 2)) return true;

    return false;
}


GameState::GameState(){
    moves = 0;
    mask  = 0;
    current_position = 0;
}


void GameState::playCol(int col){
    current_position ^= mask;
    mask |= mask + bottom_mask_col(col);
    moves++;
}


void GameState::playMove(uint64_t move){
    current_position ^= mask;
    mask |= move;
    moves++;
}


uint64_t GameState::possible() const{
    return (mask + bottom_mask) & board_mask;
}


bool GameState::isWinningMove(int col) const {
    uint64_t temp_pos = current_position; 

    // last '&' operation is done to make changes in only specified column
    temp_pos |= (mask + bottom_mask_col(col)) & column_mask(col);
    return alignment(temp_pos);
}


unsigned int GameState::play(std::string seq) {
    for(unsigned int i = 0; i < seq.size(); i++) {
        if(seq[i]==' ') break;

        int col = seq[i] - '1'; 
        if(col < 0 || col >= GameState::WIDTH || !canPlay(col) || isWinningMove(col)) return i; // invalid move
        
        playCol(col);
    }

    return seq.size();
}


uint64_t GameState::unique_key() const{
    return (current_position + mask);
}


int GameState::nbMoves() const{
    return moves;
}


uint64_t GameState::possibleNonLosingMoves() const{
    uint64_t possible_mask = possible();
    uint64_t opponent_win = opponent_winning_position();
    uint64_t forced_moves = possible_mask & opponent_win;
    if(forced_moves) {
        if(forced_moves & (forced_moves - 1)) // check if there is more than one forced move
            return 0;                           // the opponnent has two winning moves and you cannot stop him
        else possible_mask = forced_moves;    // enforce to play the single forced move
    }
    return possible_mask & ~(opponent_win >> 1);  // avoid to play below an opponent winning spot
}


bool GameState::canWinNext() const{
    return winning_position() & possible();
}


uint64_t GameState::compute_winning_position(uint64_t position, uint64_t mask) {
    // vertical;
    uint64_t r = (position << 1) & (position << 2) & (position << 3);

    //horizontal
    uint64_t p = (position << (HEIGHT+1)) & (position << 2*(HEIGHT+1));
    r |= p & (position << 3*(HEIGHT+1));
    r |= p & (position >> (HEIGHT+1));
    p = (position >> (HEIGHT+1)) & (position >> 2*(HEIGHT+1));
    r |= p & (position << (HEIGHT+1));
    r |= p & (position >> 3*(HEIGHT+1));

    //diagonal 1
    p = (position << HEIGHT) & (position << 2*HEIGHT);
    r |= p & (position << 3*HEIGHT);
    r |= p & (position >> HEIGHT);
    p = (position >> HEIGHT) & (position >> 2*HEIGHT);
    r |= p & (position << HEIGHT);
    r |= p & (position >> 3*HEIGHT);

    //diagonal 2
    p = (position << (HEIGHT+2)) & (position << 2*(HEIGHT+2));
    r |= p & (position << 3*(HEIGHT+2));
    r |= p & (position >> (HEIGHT+2));
    p = (position >> (HEIGHT+2)) & (position >> 2*(HEIGHT+2));
    r |= p & (position << (HEIGHT+2));
    r |= p & (position >> 3*(HEIGHT+2));

    return r & (board_mask ^ mask);
}
