#!/bin/bash

# echo $1
# echo $2

# echo $1

# for i in $(seq 1 20);
# do
#     python scripts/11_reddit_simulation.py --model-name qwen --time-steps $1 --subreddit 3 --topic $i --clock-factor 60

# done

for i in 1 6;
do
    for j in $(seq 1 20);
    do
    	python scripts/12_reddit_simulation_join.py --model-name qwen --time-steps $1 --subreddit "$i" --topic $j --clock-factor 60
    
    done
done

# echo $1

# for i in $(seq 1 6);
# do
#     python scripts/11_reddit_simulation_multitopic.py --model-name qwen --time-steps $1 --persona-file $i # --seed-post $j
# done