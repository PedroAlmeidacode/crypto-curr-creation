# crypto-curr-creation

- Run one flask terminal for each node (3 terminals, 3 nodes)
---
- use **POST** ```/connect_node``` and insert the other two nodes like ```nodes.json```
- use **GET** ```/get_chain``` to check your chain
- use **POST** ```/add_transaction``` like ```transaction.json``` to add a new transaction
- use **GET** ```/mine_block``` to add some transactions to a block, and receive reward for mining
- use **GET** ```/replace_chain``` to use concensus and update your chain to the longest one
