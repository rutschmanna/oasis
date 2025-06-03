#!/bin/bash

for i in $(seq 1 $1);
do
	python scripts/reddit_simulation.py --model-name qwen --time-steps 16

done

