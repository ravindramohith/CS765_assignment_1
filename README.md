# CS 765 Assigment-1

## **Environment:**
Make sure python v3 is installed on your system.

## **Running instructions:**
- basic command to run event simulator:

`$ python3 simulator.py --peers [PEERS] --z0 [Z0] --z1 [Z1] --transaction-mean-gap [TRANSATIONMEANGAP]`

- for printing blockchain:

`$ python3 simulator.py --peers [PEERS] --z0 [Z0] --z1 [Z1] --transaction-mean-gap [TRANSATIONMEANGAP] --print-blockchain`

- for visualizing the blockchain:

`$ python3 simulator.py --peers [PEERS] --z0 [Z0] --z1 [Z1] --transaction-mean-gap [TRANSATIONMEANGAP] --visualize-blockchain` 

**Note: If u want to print and visualize, add both `--print-blockchain` and `--visualize-blockchain` flags to the basic command (order dosen't matter).

PEERS - No.of peers

Z0 - z0 probability of low speed distribution

Z1 - z1 probability of low CPU speed distribution

TRANSACTIONMEANGAP - transaction mean time.

