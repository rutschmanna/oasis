#!/bin/bash

# performs 10 simulation runs for the control (1&6), moderation (2&5), and incentives (3&4) conditino a 20 topics
for r in $(seq 1 10);
do
    for i in 1 6;
    do
        for j in $(seq 1 20);
        do
        	python scripts/14_sim_control.py --model-name qwen --time-steps $1 --subreddit "$i" --topic $j --clock-factor 60 --n-run $r
        
        done
    done
done

for r in $(seq 1 10);
do
    for i in 2 5;
    do
        for j in $(seq 1 20);
        do
        	python scripts/14_sim_moderation.py --model-name qwen --time-steps $1 --subreddit "$i" --topic $j --clock-factor 60 --n-run $r
        
        done
    done
done

for r in $(seq 1 10);
do
    for i in 3 4;
    do
        for j in $(seq 1 20);
        do
        	python scripts/14_sim_incentives.py --model-name qwen --time-steps $1 --subreddit "$i" --topic $j --clock-factor 60 --n-run $r
        
        done
    done
done