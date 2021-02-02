aws ec2 describe-instances --query 'Reservations[*].Instances[*].{Instance:InstanceId,Subnet:SubnetId}' --output json --profile BDP-PROD


