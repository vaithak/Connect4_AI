#ifndef TRANSPOSITIONTABLE_H
#define TRANSPOSITIONTABLE_H

#include <vector>
#include<cassert>


// Reference: http://blog.gamesolver.org/solving-connect-four/07-transposition-table/
class TranspositionTable {
  private:

  struct Entry {
    uint64_t key: 56; // use 56-bit keys
    uint8_t val;      // use 8-bit values
  };                  // overall sizeof(Entry) = 8 bytes

  std::vector<Entry> T;

  unsigned int index(uint64_t key) const {
    return key%T.size();
  }

  public:

  TranspositionTable(unsigned int size): T(size) {
    assert(size > 0);
  }

  /*
   * Empty the Transition Table.
   */
  void reset() { // fill everything with 0, because 0 value means missing data
    memset(&T[0], 0, T.size()*sizeof(Entry));
  }


  void put(uint64_t key, uint8_t val) {
    unsigned int i = index(key); // compute the index position
    T[i].key = key;              // and overide any existing value.
    T[i].val = val;       
  }


  uint8_t get(uint64_t key) const {
    unsigned int i = index(key);  // compute the index position
    if(T[i].key == key) 
      return T[i].val;            // and return value if key matches
    else 
      return 0;                   // or 0 if missing entry
  }

};

#endif
