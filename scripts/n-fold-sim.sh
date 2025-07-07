#!/bin/bash

# echo $1
# echo $2

# for i in $(seq 1 6);
# do
#     for j in $(seq 1 20);
#     do
#     	python scripts/10_reddit_simulation.py --model-name qwen --time-steps $1 --persona-file "$i" --seed-post $j
    
#     done
# done

echo $1

for i in $(seq 1 20);
do
    python scripts/10_reddit_simulation.py --model-name qwen --time-steps $1 --persona-file "1" --seed-post $i

done

# echo $1

# for i in $(seq 1 6);
# do
#     python scripts/11_reddit_simulation_multitopic.py --model-name qwen --time-steps $1 --persona-file $i # --seed-post $j
# done