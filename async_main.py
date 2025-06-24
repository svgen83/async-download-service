import asyncio


async def main():
    archive_bytes = b''
    proc = await asyncio.create_subprocess_shell(
            'zip -r - \photo',
            stdout=asyncio.subprocess.PIPE)
    while not proc.stdout.at_eof():
        chunk = await proc.stdout.read(102400)
        archive_bytes += chunk
        await asyncio.sleep(1)
    return archive_bytes

 
archive=asyncio.run(main())

with open('archive.zip', 'wb') as arc:
            arc.write(archive)

