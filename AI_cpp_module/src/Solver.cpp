#include "Solver.h"
#include <fstream>
#include <string>
#include <sstream>
#include <iostream>

using namespace Connect4_AI;

struct moveEntry{
    uint64_t move;
    int score;
};


void add_move_to_sorted_array(moveEntry array[], moveEntry newEntry, int index){
    while(index && (array[index-1].score < newEntry.score)){
        array[index] = array[index-1];
        index--;
    }
    array[index] = newEntry;
}


void Solver::reset(){
    nodeCount = 0;
    cache.reset();
}


Solver::Solver() : cache(8388739){
    reset();
    nodeCount = 0;
    for(int i=0; i<GameState::WIDTH; i++){
        // static move ordering
        columnOrder[i] = (GameState::WIDTH/2) + ((1-2*(i%2))*(i+1)/2);
    }
}


Solver::Solver(std::string filename) : cache(8388739){
    reset();
    nodeCount = 0;
    for(int i=0; i<GameState::WIDTH; i++){
        // static move ordering
        columnOrder[i] = (GameState::WIDTH/2) + ((1-2*(i%2))*(i+1)/2);
    }

    fixed_cache.clear();
    std::ifstream fin(filename);
    if(fin){
        std::string line;

        while(std::getline(fin, line)){
            std::string moves, score;
            std::istringstream iss(line, std::istringstream::in);
            iss>>moves;
            iss>>score;

            GameState GS;
            if(GS.play(moves) != moves.size()){
                std::cerr << moves << ": Invalid move " << (GS.nbMoves()+1) << " \"" << moves << "\"" << std::endl;
            }
            else{
                fixed_cache[GS.unique_key()] = stoi(score);
            }
        }
    }
    else{
        std::cerr<<"Can't open file: "<<filename<<std::endl;
    }
}


int Solver::solve(const GameState &GS) {
    nodeCount = 0;

    if(GS.canWinNext()) // check if win in one move as the Negamax function does not support this case.
        return (GameState::WIDTH*GameState::HEIGHT+1 - GS.nbMoves())/2;

    uint64_t curr_key = GS.unique_key();
    if(fixed_cache.find(curr_key) != fixed_cache.end())
        return fixed_cache[curr_key];

    int min = -(GameState::WIDTH*GameState::HEIGHT   - GS.nbMoves())/2;
    int max =  (GameState::WIDTH*GameState::HEIGHT+1  - GS.nbMoves())/2;

    while(min < max) { // iteratively narrow the min-max exploration window -- similar to binary search
        int med = min + (max - min)/2;

        // these two lines causes a performance boost
        if(med <= 0 && min/2 < med) med = min/2;
        else if(med >= 0 && max/2 > med) med = max/2;

        int res = negamax(GS, med, med + 1);   // use a null depth window to know if the actual score is greater or smaller than med
        if(res <= med) max = res;
        else min = res;
    }
    return min;
}


unsigned long long Solver::getNodeCount() {
    return nodeCount;
}

int Solver::negamax(const GameState& GS, int alpha, int beta){
    nodeCount++;

    uint64_t curr_key = GS.unique_key();
    if(nodeCount<2000000 && fixed_cache.find(curr_key) != fixed_cache.end())
        return fixed_cache[curr_key];
    
    uint64_t next_moves = GS.possibleNonLosingMoves();
    if(next_moves == 0)     // if no possible non losing move, opponent wins next move
        return -(GameState::WIDTH*GameState::HEIGHT - GS.nbMoves())/2;

    if(GS.nbMoves() >= GameState::WIDTH*GameState::HEIGHT-2) // Game Tied
        return 0;

    int min = -(GameState::WIDTH*GameState::HEIGHT - 2 - GS.nbMoves())/2;    // lower bound of score as opponent cannot win next move
    if(alpha < min) {
        alpha = min;                    // there is no need to keep beta above our max possible score.
        if(alpha >= beta) return alpha;  // prune the exploration if the [alpha;beta] window is empty.
    }


    int max = (GameState::WIDTH*GameState::HEIGHT-1 - GS.nbMoves())/2;   // upper bound of our score as we cannot win immediately
    int cached_upper_bound = cache.get(curr_key);
    if(cached_upper_bound)
        max = cached_upper_bound-50;   // as we can't go above cached_upper_bound

    if(beta > max) {
        beta = max;
        if(alpha >= beta) return beta;
    }

    int moves_num = 0;
    moveEntry dynamicOrder[GameState::WIDTH];
    for(int i=0; i<GameState::WIDTH; i++){
        if(uint64_t move = next_moves & GameState::column_mask(columnOrder[i])){
            add_move_to_sorted_array(dynamicOrder, {move, GS.moveScore(move)}, moves_num);
            moves_num++;
        }
    }


    for (int i = 0; i<moves_num; i++) { 
        GameState temp_GS(GS);     // because we don't want to change original game state
        temp_GS.playMove(dynamicOrder[i].move);
        int temp_score = -negamax(temp_GS, -beta, -alpha);

        if(temp_score >= beta) return temp_score;

        if(temp_score > alpha) alpha = temp_score;     // as or new lower bound will increase now  
    }

    cache.put(curr_key, alpha + 50); // save the upper bound of the GameState
    return alpha;

}
