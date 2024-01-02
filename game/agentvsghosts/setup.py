from cx_Freeze import setup, Executable

setup(
    name="agentvsghosts",
    version="1.0",
    description="This is the version 1.0 of AGENT V.S. GHOSTS",
    executables=[Executable("agentvsghosts.py")],
)