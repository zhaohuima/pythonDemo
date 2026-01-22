#!/bin/bash
# Auto-deploy wrapper that provides automatic responses

# Provide responses: n (don't update versions), n (don't create swap), n (don't fix nginx), y (continue deployment)
(echo "n"; sleep 2; echo "n"; sleep 2; echo "n"; sleep 2; echo "y") | ./deploy_to_ec2.sh
