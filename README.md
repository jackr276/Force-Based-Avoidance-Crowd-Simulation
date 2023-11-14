# Crowd Simulation using a Force-Based Avoidance Algorithm
Authors: [Jack Robbins](https://github.com/jackr276) and [Randall Tarazona](https://github.com/Randall543)

## [favoid.py](https://github.com/jackr276/Force-Based-Avoidance-Crowd-Simulation/blob/main/favoid.py)
This program uses a force based avoidance algorithm to simulate a crowd. In this implementation, every agent is checked against every other agent, leading to
O(n<sup>2</sup>) time complexity. This will be improved apon in **shash.py**.

## [fps.py](https://github.com/jackr276/Force-Based-Avoidance-Crowd-Simulation/blob/main/fps.py)
This program is an exact copy of **favoid.py**, with a simple terminal based FPS counter added in. This FPS counter will allow us to compare efficiency between
our two implementations of crowd based avoidance.

## [shash.py](https://github.com/jackr276/Force-Based-Avoidance-Crowd-Simulation/blob/main/shash.py)
This program implements a force based avoidance algorithm on top of a spatial hash to greatly improve efficiency and fps from **favoid.py**. This program
also includes the same FPS counter as **fps.py**, so efficiency can be compared.

### Configuration Instructions
  1. Download the desired *.py files and [requirements.txt](https://github.com/jackr276/Position-Based-Dynamics/blob/main/requirements.txt)
  2. Create a python [virtual environment](https://docs.python.org/3/library/venv.html)
  3. Activate your new python [virtual environment](https://docs.python.org/3/library/venv.html)
  4. Run ```pip -r install requirements.txt```
  5. Run the desired file with the command ```python filename.py```
  6. Enjoy the crowd simulations!
