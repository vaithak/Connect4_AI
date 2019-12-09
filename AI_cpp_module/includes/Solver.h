#ifndef SOLVER_H
#define SOLVER_H

#include "GameState.h"
#include "TranspositionTable.h"
#include <unordered_map>

namespace Connect4_AI{
    class Solver {
        private:
            unsigned long long nodeCount;     // -- for testing purposes
            int columnOrder[GameState::WIDTH];
            TranspositionTable cache;
            std::unordered_map<uint64_t, int> fixed_cache;

            /**
             * Recursively score connect 4 GameState using negamax variant of alpha-beta algorithm.
             * @param: alpha < beta, a score window within which we are evaluating the GameState.
             *
             * @return the exact score, an upper or lower bound score depending of the case:
             * - if actual score of GameState <= alpha then actual score <= return value <= alpha
             * - if actual score of GameState >= beta then beta <= return value <= actual score
             * - if alpha <= actual score <= beta then return value = actual score
             */
            int negamax(const GameState& GS, int alpha, int beta);

        public:
            Solver();
            Solver(std::string filename);
            void reset();
            int solve(const GameState &GS);
            unsigned long long getNodeCount(); 
    };
}

#endif