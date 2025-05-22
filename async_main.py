import asyncio
import glob
#import subprocess

async def run():
    proc = await asyncio.create_subprocess_shell(
        'zip -r - photo/*',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    
    archive = await proc.stdout.read()
    
    with open('archive.zip', 'wb') as arc:
        arc.write(archive)

asyncio.run(run())
