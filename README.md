# bark

CLI client for communicating with satellites on the Iridium Satellite Network using the NearSpace Launch API

## Requirements

- git (for cloning the repo)
- python 3.8+

## Setup

Clone `bark` repo

```bash
git clone git@github.com:ODU-CGA-CubeSat/bark.git
```

Change directory to bark repo

```bash
cd bark
```

## Installation

Create a virtual environment

```bash
python3 -m venv venv
```

Activate virtual environment

```bash
. ./venv/bin/activate
```

Install python package requirements

```bash
pip install -r requirements.txt
```

Note: Alternatively, you can skip the above steps by running the [sealion-workspace-image](https://github.com/odu-cga-cubesat/sealion-workspace-image)

## Example usage

Print help text

```bash
./bark.py
```

Set user email, API key, & mission id

```bash
./bark.py --set-email your_email@example.com --set-api-key 173467321476c32789777643t732v73117888732476789764376 --set-mission-id 1701
```

Display info on mission

```bash
./bark.py --info
```

List all packets on mission

```bash
./bark.py -l
```
