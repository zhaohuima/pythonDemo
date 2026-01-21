#!/bin/bash
# Wrapper script to auto-confirm deploy_to_staging.sh prompts

# Use expect to handle interactive prompts
/usr/bin/expect <<'EOF'
set timeout 1200
spawn bash deploy_to_staging.sh

# Handle first prompt about uncommitted changes
expect {
    "是否继续部署? (y/n)" {
        send "y"
        exp_continue
    }
    "所有检查完成，是否继续部署? (y/n)" {
        send "y"
        exp_continue
    }
    timeout {
        puts "Timeout waiting for prompt"
        exit 1
    }
    eof
}

wait
EOF
