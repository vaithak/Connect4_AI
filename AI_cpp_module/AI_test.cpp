#include <iostream>
#include <fstream>
#include <sys/time.h>
#include <vector>

#include "Solver.h"

/*
 * Get micro-second precision timestamp
 * uses unix gettimeofday function
 */

unsigned long long getTimeMicrosec() {
  timeval NOW;
  gettimeofday(&NOW, NULL);
  return NOW.tv_sec*1000000LL + NOW.tv_usec;    
}


/*
 * Main function.
 * Reads Connect 4 positions, line by line, from standard input 
 * and writes one line per position to standard output containing:
 *  - score of the position
 *  - number of nodes explored
 *  - time spent in microsecond to solve the position.
 *
 *  Any invalid position (invalid sequence of move, or already won game) 
 *  will generate an error message to standard error and an empty line to standard output.
 */
int main() {
    Connect4_AI::Solver solver("score_data.txt");
    // Connect4_AI::Solver solver;
    std::string line;
    
    for(int l = 1; std::getline(std::cin, line); l++) {
        Connect4_AI::GameState GS;
        if(GS.play(line) != line.size()){
            std::cerr << "Line << " << l << ": Invalid move " << (GS.nbMoves()+1) << " \"" << line << "\"" << std::endl;
        }
        else{
            solver.reset();
            unsigned long long start_time = getTimeMicrosec();
            int score = solver.solve(GS);
            unsigned long long end_time = getTimeMicrosec();
            std::cout << line << " " << score << " " << solver.getNodeCount() << " " << (end_time - start_time);
        }
        std::cout << std::endl;
    }
    return 0;
}