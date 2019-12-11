CXX=g++
CXXFLAGS=--std=c++14 -W -Wall -O3 -I includes/ -DNDEBUG
HEADERS=includes/GameState.h includes/Solver.h includes/TranspositionTable.h

SRCS=AI_test.cpp src/Solver.cpp src/GameState.cpp
OBJS=$(subst .cpp,.o,$(SRCS))

c4solver:$(OBJS) $(HEADERS)
	$(CXX) -flto -o c4solver $(OBJS)

clean:
	rm -f *.o c4solver src/*.o


