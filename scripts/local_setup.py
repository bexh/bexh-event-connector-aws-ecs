import subprocess


cmd = """
awslocal kinesis create-stream \
    --stream-name bexh-incoming-bets \
    --shard-count 1
"""
try:
    print(cmd)
    print(subprocess.getoutput(cmd))
except Exception as e:
    print("topic already exists", e)

cmd = """
awslocal kinesis create-stream \
    --stream-name bexh-outgoing-events \
    --shard-count 1
"""
try:
    print(cmd)
    print(subprocess.getoutput(cmd))
except Exception as e:
    print("topic already exists", e)

cmd = """
awslocal kinesis create-stream \
    --stream-name bexh-outgoing-bets \
    --shard-count 1
"""
try:
    print(cmd)
    print(subprocess.getoutput(cmd))
except Exception as e:
    print("topic already exists", e)
